import openai
import os
import argparse
import fitz
import json
import time
from pathlib import Path
from dotenv import load_dotenv

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import cfg

# Load environment variables from .env file
load_dotenv()

client = openai.OpenAI(
    api_key=os.environ.get(cfg.API_KEY_ENV),
    base_url=cfg.API_BASE_URL,
)

# Pull all user-configurable settings from cfg (sourced from user_config.json)
BOOK_PATHS = cfg.BOOK_PATHS
CHAPTER_PAGE_MAP = cfg.CHAPTER_PAGE_MAP


# ── TEXTBOOK EXTRACTION ────────────────────────────────────────────────────────


def extract_chapter_cached(book: str, chapter: int) -> str:
    cache_path = Path(f"textbooks/extracted/{book.lower()}_ch{chapter}.txt")
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")
    if str(chapter) not in [str(k) for k in CHAPTER_PAGE_MAP.get(book, {})]:
        return ""
    doc = fitz.open(BOOK_PATHS[book])

    start, end = None, None
    for k, v in CHAPTER_PAGE_MAP[book].items():
        if str(k) == str(chapter):
            start, end = v
            break

    text = ""
    for page_num in range(start - 1, min(end, doc.page_count)):
        text += doc[page_num].get_text()
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(text, encoding="utf-8")
    return text


def build_textbook_content(topic: dict) -> str:
    """
    Builds the full textbook context block passed to the LLM.

    Since Claude 4.6 has a massive context window, we now pass the ENTIRE
    extracted chapter rather than cropping it, ensuring the LLM has
    every piece of context available.
    """
    sections = []
    found_any = False

    for source in topic.get("textbook_sources", []):
        book = source["book"]
        priority = source.get("priority", "support")

        for chapter in source.get("chapters", []):
            raw = extract_chapter_cached(book, chapter)

            if not raw:
                sections.append(
                    f"[WARNING] [EXTRACTION FAILED: {book} ch.{chapter} — "
                    f"check textbooks/extracted/ or CHAPTER_PAGE_MAP]"
                )
                continue

            # Pass the full chapter text
            excerpt = raw

            if not excerpt.strip():
                sections.append(
                    f"[WARNING] [EMPTY EXCERPT: {book} ch.{chapter} — "
                    f"keyword match failed. "
                    f"Check topic name spelling vs textbook headings.]"
                )
                continue

            found_any = True
            sections.append(
                f"{'=' * 60}\n"
                f"SOURCE: {book} | Chapter {chapter} "
                f"| Priority: {priority.upper()}\n"
                f"{'=' * 60}\n"
                f"{excerpt}"
            )

    if not found_any:
        sections.append(
            "[WARNING] [CRITICAL: No textbook content was extracted for "
            "this topic. Note generation will be unreliable. "
            "Run extract_textbook_sections.py first and verify "
            "CHAPTER_PAGE_MAP covers all mapped chapters.]"
        )

    return "\n\n".join(sections)


# ── PROMPT BUILDER ─────────────────────────────────────────────────────────────


def build_prompt(topic: dict, textbook_content: str) -> str:
    note_type = topic.get("note_type", "concept")
    prereqs = topic.get("prerequisites", [])
    prereq_links = " ".join([f"[[{p}]]" for p in prereqs])
    importance = topic.get("interview_importance", 5)
    difficulty = topic.get("difficulty", "medium")

    header = cfg.get_note_header(note_type, topic["playlist_day"])
    header += f"""

Topic: {topic["topic"]}
Section: {topic["section"]}
Playlist Day: {topic["playlist_day"]}
Difficulty: {difficulty}
Interview Importance: {importance}/10
Note Type: {note_type}
Prerequisites: {prereqs}

NON-NEGOTIABLE RULES:
{cfg.SHARED_RULES}
"""

    template = (
        f"\n# {topic['topic']}\n\n"
        + cfg.get_note_template(
            note_type,
            importance=importance,
            prereqs=str(prereqs),
        )
        + f"\n\n---\nPrerequisites: {prereq_links}\n"
    )

    # ── Assemble ────────────────────────────────────────────────
    return (
        header
        + "\n"
        + template
        + f"\n\n{'=' * 60}\n"
        + "TEXTBOOK CONTENT — USE ONLY THIS AS YOUR SOURCE:\n"
        + f"{'=' * 60}\n\n"
        + textbook_content
    )


def build_merged_textbook_content(group_topics: list) -> str:
    sources_map = {}
    for topic in group_topics:
        role = topic.get("merge_role", "unknown")
        if not role:
            role = "unknown"
        for source in topic.get("textbook_sources", []):
            book = source["book"]
            priority = source.get("priority", "support")
            for chapter in source.get("chapters", []):
                key = (book, str(chapter))
                if key not in sources_map:
                    sources_map[key] = {"roles": set(), "priority": priority}
                sources_map[key]["roles"].add(role)
                if priority == "primary":
                    sources_map[key]["priority"] = "primary"
                elif (
                    priority == "support"
                    and sources_map[key]["priority"] == "reference"
                ):
                    sources_map[key]["priority"] = "support"

    sections = []
    found_any = False
    for (book, chapter), data in sources_map.items():
        raw = extract_chapter_cached(book, chapter)
        if not raw:
            sections.append(f"[WARNING] [EXTRACTION FAILED: {book} ch.{chapter}]")
            continue
        found_any = True
        roles_str = ", ".join(sorted(list(data["roles"])))
        sections.append(
            f"{'=' * 60}\n"
            f"SOURCE: {book} | Chapter {chapter} | Priority: {data['priority'].upper()} | Roles: {roles_str}\n"
            f"{'=' * 60}\n"
            f"{raw}"
        )

    if not found_any:
        sections.append(
            "[WARNING] [CRITICAL: No textbook content was extracted for this group.]"
        )
    return "\n\n".join(sections)


def get_merged_sections(group_topics: list) -> list:
    roles = [t.get("merge_role") for t in group_topics if t.get("merge_role")]
    sections = []
    if "intuition" in roles:
        sections.append(
            (
                "Intuition",
                "Provide intuition based on the textbook. Explain the core idea in plain English.",
            )
        )
    math_roles = [r for r in roles if r.startswith("mathematics")]
    if math_roles:
        sections.append(
            (
                "Mathematical Formulation",
                "Full derivation or key equations based on the textbook. Include all math-related angles provided. Source every equation.",
            )
        )
    if "implementation" in roles or "code" in roles:
        sections.append(
            (
                "Implementation",
                "Provide code examples from the textbook. Comment every non-obvious line.",
            )
        )
    if "extension" in roles:
        sections.append(
            (
                "Extended Case",
                "Explain how this extends to multiple features or general cases.",
            )
        )
    if "assumptions" in roles:
        sections.append(
            (
                "Assumptions",
                "List the assumptions underlying this method based on the textbook.",
            )
        )
    if "key_points" in roles:
        sections.append(("Key Points", "Summarize the key points."))
    if "hyperparameters" in roles:
        sections.append(("Hyperparameters", "List and explain hyperparameters."))
    if "visualization" in roles:
        sections.append(
            ("Visualization Notes", "Describe how to visualize this concept.")
        )

    other_roles = set(roles) - {
        "intuition",
        "mathematics",
        "implementation",
        "code",
        "extension",
        "assumptions",
        "key_points",
        "hyperparameters",
        "visualization",
    }
    other_roles = {r for r in other_roles if not r.startswith("mathematics")}
    for r in sorted(list(other_roles)):
        title = r.replace("_", " ").title()
        sections.append((title, f"Explain {title} based on the textbook."))

    return sections


def build_section_prompt(
    merge_group: str,
    group_topics: list,
    section_title: str,
    section_instruction: str,
    previous_content: str,
    textbook_content: str,
) -> str:
    group_name = merge_group.replace("_", " ").title()
    days = [t["playlist_day"] for t in group_topics]

    header = f"""You are generating ONE SECTION of an Obsidian markdown companion note for a MERGED topic.
This note covers multiple days from the playlist that belong to the same concept.

Group Topic: {group_name}
Playlist Days: {days}

You are specifically writing the section: ## {section_title}
Instruction for this section: {section_instruction}

NON-NEGOTIABLE RULES:
- Use ONLY the textbook content provided at the bottom of this prompt.
- Do NOT use your training data or memory for any fact or formula.
- Every non-trivial claim must end with its source in parentheses: (HOML ch.4) or (ISL ch.3).
- All mathematics must be LaTeX: $inline$ or $$block$$.
- Output ONLY the markdown for this specific section, starting with the header `## {section_title}`.
- Do NOT output preamble or explanation.
- Maximize depth. Do not skip textbook details relevant to this section.
"""

    if previous_content:
        header += f"\n\nFor context, here is what has ALREADY been generated for this note (do NOT repeat this):\n{'=' * 40}\n{previous_content}\n{'=' * 40}\n"

    return (
        header
        + f"\n\n{'=' * 60}\n"
        + "TEXTBOOK CONTENT — USE ONLY THIS AS YOUR SOURCE:\n"
        + f"{'=' * 60}\n\n"
        + textbook_content
    )


# ── VAULT PATH ─────────────────────────────────────────────────────────────────


def get_vault_path_merged(first_topic: dict, merge_group: str) -> Path:
    from pathlib import Path

    section = first_topic.get("section", "Foundations")
    safe_section = section.replace(" (Unsupervised Learning)", "").replace(" ", "_")
    folder = f"KB_Obsidian/{safe_section}/"
    return Path(folder) / f"{merge_group}.md"


def get_vault_path(topic: dict) -> Path:
    section = topic.get("section", "Foundations")
    # Clean section name to make a nice directory name
    safe_section = section.replace(" (Unsupervised Learning)", "").replace(" ", "_")
    folder = f"KB_Obsidian/{safe_section}/"
    slug = topic["slug"]
    day = topic.get("playlist_day", "X")
    return Path(folder) / f"day_{day}_{slug}.md"


# ── PROGRESS + FAILURE TRACKING ───────────────────────────────────────────────


def load_topics() -> list:
    with open("topics.json") as f:
        return json.load(f)


def load_progress() -> dict:
    path = Path("notes_progress.json")
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def save_progress(progress: dict):
    with open("notes_progress.json", "w") as f:
        json.dump(progress, f, indent=2)


def log_failure(topic: dict, error: str):
    path = Path("failed_topics.json")
    failures = []
    if path.exists():
        with open(path) as f:
            failures = json.load(f)
    failures.append(
        {"topic": topic["topic"], "day": topic["playlist_day"], "error": error}
    )
    with open(path, "w") as f:
        json.dump(failures, f, indent=2)


def load_formulas() -> list:
    path = Path("formulas.json")
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return []


def load_mappings() -> dict:
    import re

    mapping = {}
    path = Path("mapping.txt")
    if not path.exists():
        return mapping
    current_day = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            m = re.match(r"^(\d+)\.\s+(.*)", line)
            if m:
                current_day = int(m.group(1))
                mapping[current_day] = {}
            elif current_day is not None and line.startswith("["):
                m2 = re.match(r"^\[([A-Z]+)\s+ch\.([^\]]+)\]\s*(.*)", line)
                if m2:
                    book = m2.group(1)
                    mapping[current_day][book] = m2.group(3)
    return mapping


# ── CORE GENERATION ────────────────────────────────────────────────────────────


def generate_note(
    topic: dict, all_topics: list, formulas: list, mappings: dict, dry_run: bool = False
) -> bool:
    progress = load_progress()

    merge_group = topic.get("merge_group")
    if merge_group:
        group_topics = sorted(
            [t for t in all_topics if t.get("merge_group") == merge_group],
            key=lambda x: x["playlist_day"],
        )
        days = [t["playlist_day"] for t in group_topics]
        group_key = f"group_{merge_group}"

        if progress.get(group_key) == "done":
            print(
                f"  [skip] Day {topic['playlist_day']}: already covered in {merge_group}.md"
            )
            return True

        textbook_content = build_merged_textbook_content(group_topics)
        vault_path = get_vault_path_merged(group_topics[0], merge_group)

        if dry_run:
            print(f"\n  [dry-run] MERGED GROUP: {merge_group} (Days {days})")
            print(f"    Output: {vault_path}")
            return True

        print(f"\n  Generating MERGED: Days {days} -> {merge_group}.md")

        try:
            sections_to_generate = get_merged_sections(group_topics)
            group_name = merge_group.replace("_", " ").title()
            final_note = f"# {group_name}\n\n"

            print(f"    (Iterative Generation: {len(sections_to_generate)} sections)")

            for sec_title, sec_inst in sections_to_generate:
                print(f"    -> Generating section: {sec_title}...")
                prompt = build_section_prompt(
                    merge_group,
                    group_topics,
                    sec_title,
                    sec_inst,
                    final_note,
                    textbook_content,
                )

                response = client.chat.completions.create(
                    model=cfg.MODEL,
                    max_tokens=cfg.MERGED_NOTE_MAX_TOKENS,
                    messages=[{"role": "user", "content": prompt}],
                )

                section_content = response.choices[0].message.content.strip()
                final_note += section_content + "\n\n"
                time.sleep(cfg.RATE_LIMIT_SLEEP)

            prereqs = set()
            for t in group_topics:
                prereqs.update(t.get("prerequisites", []))
            prereq_links = " ".join([f"[[{p}]]" for p in sorted(list(prereqs))])

            final_note += f"## Related Topics\n[[backlinks]] for prerequisites only.\n\n---\nPrerequisites: {prereq_links}\n"

            vault_path.parent.mkdir(parents=True, exist_ok=True)
            vault_path.write_text(final_note, encoding="utf-8")

            progress[group_key] = "done"
            for d in days:
                progress[f"day_{d}"] = "done"
            save_progress(progress)

            print(f"  [OK] Saved -> {vault_path}")
            print(f"  Merged: Days {', '.join(map(str, days))} -> {merge_group}.md")
            print_group_summary(
                merge_group,
                group_topics,
                all_topics,
                formulas,
                mappings,
                vault_path,
                is_brief=False,
            )
            return True

        except Exception as e:
            for t in group_topics:
                log_failure(t, f"Group {merge_group} failed: {str(e)}")
            print(f"  [FAILED] {e} — logged to failed_topics.json")
            return False

    topic_key = f"day_{topic['playlist_day']}"

    if progress.get(topic_key) == "done":
        print(
            f"  [skip] Day {topic['playlist_day']}: "
            f"{topic['topic']} — already generated"
        )
        print_topic_summary(topic, all_topics, formulas, mappings, is_brief=False)
        return True

    textbook_content = build_textbook_content(topic)
    vault_path = get_vault_path(topic)

    if dry_run:
        sources = [
            f"{s['book']} ch.{c}"
            for s in topic.get("textbook_sources", [])
            for c in s.get("chapters", [])
        ]
        has_content = (
            "YES"
            if "EXTRACTION FAILED" not in textbook_content
            and "CRITICAL" not in textbook_content
            and textbook_content.strip()
            else "NO — run extract_textbook_sections.py first"
        )
        print(f"\n  [dry-run] Day {topic['playlist_day']}: {topic['topic']}")
        print(f"    Note type:   {topic.get('note_type', 'concept')}")
        print(f"    Section:     {topic['section']}")
        print(f"    Difficulty:  {topic['difficulty']}")
        print(f"    Importance:  {topic.get('interview_importance')}/10")
        print(f"    Sources:     {', '.join(sources) or 'none mapped'}")
        print(f"    Output:      {vault_path}")
        print(f"    Content:     {has_content}")
        return True

    print(
        f"\n  Generating: Day {topic['playlist_day']} — "
        f"{topic['topic']} [{topic.get('note_type', 'concept')}]"
    )

    try:
        response = client.chat.completions.create(
            model=cfg.MODEL,
            max_tokens=cfg.STANDALONE_NOTE_MAX_TOKENS,
            messages=[
                {"role": "user", "content": build_prompt(topic, textbook_content)}
            ],
        )
        note_content = response.choices[0].message.content

        vault_path.parent.mkdir(parents=True, exist_ok=True)
        vault_path.write_text(note_content, encoding="utf-8")

        progress[topic_key] = "done"
        save_progress(progress)

        print(f"  [OK] Saved -> {vault_path}")
        print_topic_summary(topic, all_topics, formulas, mappings, is_brief=False)
        time.sleep(cfg.RATE_LIMIT_SLEEP)
        return True

    except Exception as e:
        log_failure(topic, str(e))
        print(f"  [FAILED] {e} — logged to failed_topics.json")
        return False


# ── SUMMARY PRINTER ────────────────────────────────────────────────────────────

import textwrap


def compute_unlocks(topic_name: str, all_topics: list) -> list:
    unlocks = []
    for t in all_topics:
        if any(p.lower() == topic_name.lower() for p in t.get("prerequisites", [])):
            unlocks.append(t)
    unlocks.sort(key=lambda x: x.get("playlist_day", 999))
    return unlocks[:6]


def print_topic_summary(
    topic: dict,
    all_topics: list,
    formulas: list,
    mappings: dict,
    is_brief: bool = False,
):
    vault_path = get_vault_path(topic)
    day = topic.get("playlist_day", "?")

    print(f"\n  {'=' * 56}")
    print(f"    DAY {day} — {topic['topic']}")
    print(
        f"    Section: {topic.get('section', '-')}  |  Difficulty: {topic.get('difficulty', 'medium')}"
    )
    print(f"    Interview Importance: {topic.get('interview_importance') or '-'}/10")
    print(f"  {'=' * 56}\n")

    # 1. PREREQUISITES
    print("    PREREQUISITES — study these first if not done:")
    print("    ---------------------------------------------")
    prereqs = topic.get("prerequisites", [])
    if not prereqs:
        print("    [OK] No prerequisites for this topic")
    else:
        all_met = True
        for p_name in prereqs:
            p_topic = next(
                (t for t in all_topics if t["topic"].lower() == p_name.lower()), None
            )
            if p_topic:
                status = p_topic.get("status", "not_started")
                p_day = p_topic.get("playlist_day", "?")
                if status == "studied":
                    print(f"    [OK] Day {p_day} — {p_topic['topic']} [studied]")
                else:
                    print(
                        f"    [NO] Day {p_day} — {p_topic['topic']} [{status}]  <- do this first"
                    )
                    all_met = False
            else:
                print(f"    [NO] ? — {p_name} [unknown]  <- do this first")
                all_met = False
        if all_met:
            print("    [OK] All prerequisites complete")

    # 2. WHAT TO READ TODAY
    print("\n    WHAT TO READ TODAY:")
    print("    ---------------------------------------------")
    sources = topic.get("textbook_sources", [])
    if not sources:
        print("    (No textbook readings mapped for this topic)")
    else:
        grouped = {"primary": [], "support": [], "reference": []}
        for s in sources:
            pri = s.get("priority", "support")
            if pri in grouped:
                grouped[pri].append(s)

        for pri in ["primary", "support", "reference"]:
            if grouped[pri]:
                print(f"    {pri.upper()}")
                for s in grouped[pri]:
                    book = s["book"]
                    ch_str = ", ".join(map(str, s.get("chapters", [])))
                    print(f"      {book}  Chapter {ch_str}")

                    mapping_text = mappings.get(day, {}).get(book)
                    if mapping_text:
                        wrapped = textwrap.fill(
                            f"-> Topic maps to: {mapping_text}",
                            width=45,
                            subsequent_indent="          ",
                        )
                        for line in wrapped.split("\n"):
                            print(f"        {line.strip()}")
                        print("")

        if not any(s["book"] == "PRML" for s in sources):
            print("\n    (No PRML reference for this topic)")

    # 3. KEY FORMULAS
    print("\n    KEY FORMULAS FOR THIS TOPIC:")
    print("    ---------------------------------------------")
    topic_slug = topic["slug"]
    topic_formulas = [f for f in formulas if f.get("topic") == topic_slug]
    if topic_formulas:
        for f in topic_formulas:
            print(f"    {f.get('name', 'Formula')}: {f.get('latex', '')}")
    else:
        if topic.get("difficulty") == "low":
            print("    (none — low difficulty topic)")
        else:
            print("    [NEEDS REVIEW: expected formulas but none extracted]")

    # 4. WHAT THIS UNLOCKS
    print("\n    WHAT THIS UNLOCKS:")
    print("    ---------------------------------------------")
    unlocks = compute_unlocks(topic["topic"], all_topics)
    if unlocks:
        for u in unlocks:
            print(f"    -> Day {u.get('playlist_day', '?')} — {u['topic']}")
    else:
        print("    (none)")

    # 5. NOTE STATS
    print("\n    NOTE STATS:")
    print("    ---------------------------------------------")
    if vault_path.exists():
        content = vault_path.read_text(encoding="utf-8")
        body = content
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                body = parts[2]
        if not body.strip():
            print("    File exists:  [NO] Exists but is empty/unreadable")
        else:
            words = len(body.split())
            print(f"    Word count:   {words} words")
            print(f"    Length:       {len(content):,} characters")
            print(f"    Note type:    {topic.get('note_type', 'concept')}")
            print(f"    File exists:  [OK] {vault_path.as_posix()}")
    else:
        print("    File exists:  [NO] Not yet generated")
        print(f"                    Run --day {day} to generate")

    # 6. NOTE SAVED TO & OPEN IN OBSIDIAN
    if vault_path.exists():
        if not is_brief:
            print("\n    NOTE SAVED TO:")
            print("    ---------------------------------------------")
            print(f"    {vault_path.as_posix()}")

        print("\n    OPEN IN OBSIDIAN:")
        print("    ---------------------------------------------")
        try:
            rel_path_str = (
                vault_path.relative_to(vault_path.parts[0]).with_suffix("").as_posix()
            )
        except ValueError:
            rel_path_str = vault_path.with_suffix("").as_posix()
        print(f"    obsidian://open?vault={vault_path.parts[0]}&file={rel_path_str}")

    print(f"\n  {'=' * 56}\n")


def print_group_summary(
    merge_group: str,
    group_topics: list,
    all_topics: list,
    formulas: list,
    mappings: dict,
    vault_path,
    is_brief: bool = False,
):
    days = [t["playlist_day"] for t in group_topics]
    group_title = merge_group.replace("_", " ").title()
    section = group_topics[0].get("section", "-")

    print(f"\n  {'=' * 56}")
    print(f"    DAYS {', '.join(map(str, days))} — {group_title}")
    print(f"    Section: {section}  |  MERGED GROUP")
    print(f"  {'=' * 56}\n")

    # 1. PREREQUISITES
    print("    PREREQUISITES (Union) — study these first if not done:")
    print("    ---------------------------------------------")
    prereqs = set()
    for t in group_topics:
        prereqs.update(t.get("prerequisites", []))

    if not prereqs:
        print("    [OK] No prerequisites for this group")
    else:
        all_met = True
        for p_name in sorted(list(prereqs)):
            p_topic = next(
                (t for t in all_topics if t["topic"].lower() == p_name.lower()), None
            )
            if p_topic:
                status = p_topic.get("status", "not_started")
                p_day = p_topic.get("playlist_day", "?")
                if status == "studied":
                    print(f"    [OK] Day {p_day} — {p_topic['topic']} [studied]")
                else:
                    print(
                        f"    [NO] Day {p_day} — {p_topic['topic']} [{status}]  <- do this first"
                    )
                    all_met = False
            else:
                print(f"    [NO] ? — {p_name} [unknown]  <- do this first")
                all_met = False
        if all_met:
            print("    [OK] All prerequisites complete")

    # 2. WHAT TO READ
    print("\n    WHAT TO READ TODAY:")
    print("    ---------------------------------------------")
    books = {}
    for t in group_topics:
        for s in t.get("textbook_sources", []):
            b = s["book"]
            for c in s.get("chapters", []):
                if b not in books:
                    books[b] = set()
                books[b].add(str(c))

    if not books:
        print("    (No textbook readings mapped for this group)")
    else:
        for b in sorted(books.keys()):
            ch_str = ", ".join(
                sorted(
                    list(books[b]),
                    key=lambda x: float(x) if x.replace(".", "", 1).isdigit() else 999,
                )
            )
            print(f"      {b}  Chapter {ch_str}")

    # 3. NOTE STATS
    print("\n    NOTE STATS:")
    print("    ---------------------------------------------")
    if vault_path.exists():
        content = vault_path.read_text(encoding="utf-8")
        body = content
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                body = parts[2]
        if not body.strip():
            print("    File exists:  [NO] Exists but is empty/unreadable")
        else:
            words = len(body.split())
            print(f"    Word count:   {words} words")
            print(f"    Length:       {len(content):,} characters")
            print(f"    Note type:    MERGED GROUP")
            print(f"    File exists:  [OK] {vault_path.as_posix()}")
    else:
        print("    File exists:  [NO] Not yet generated")

    if vault_path.exists():
        if not is_brief:
            print("\n    NOTE SAVED TO:")
            print("    ---------------------------------------------")
            print(f"    {vault_path.as_posix()}")

        print("\n    OPEN IN OBSIDIAN:")
        print("    ---------------------------------------------")
        try:
            rel_path_str = (
                vault_path.relative_to(vault_path.parts[0]).with_suffix("").as_posix()
            )
        except ValueError:
            rel_path_str = vault_path.with_suffix("").as_posix()
        print(f"    obsidian://open?vault={vault_path.parts[0]}&file={rel_path_str}")

    print(f"\n  {'=' * 56}\n")


def print_batch_summary(
    selected_topics: list, all_topics: list, is_brief: bool, generated_count: int = 0
):
    if not selected_topics:
        return

    days = [t.get("playlist_day") for t in selected_topics if t.get("playlist_day")]
    if not days:
        return
    min_day, max_day = min(days), max(days)
    day_str = f"Day {min_day}" if min_day == max_day else f"Days {min_day}-{max_day}"
    section = selected_topics[0].get("section", "Misc")

    print(f"\n  {'=' * 56}")
    print(f"    BATCH COMPLETE — {day_str} ({section})")
    print(f"  {'=' * 56}\n")

    total = len(selected_topics)

    if is_brief:
        existing = sum(1 for t in selected_topics if get_vault_path(t).exists())
        print(f"    Notes already generated:  {existing} / {total}")
        missing = total - existing
        if missing > 0:
            missing_days = [
                str(t.get("playlist_day"))
                for t in selected_topics
                if not get_vault_path(t).exists()
            ]
            print(
                f"    Notes not yet generated:  {missing} / {total}  (Days {', '.join(missing_days)})"
            )
    else:
        print(f"    Notes generated: {generated_count}")
        print(f"    Failed:          {total - generated_count}")

    print("\n    PREREQUISITES NOT YET STUDIED ACROSS THIS BATCH:")
    missing_prereqs = {}
    for t in selected_topics:
        for p_name in t.get("prerequisites", []):
            p_topic = next(
                (tp for tp in all_topics if tp["topic"].lower() == p_name.lower()), None
            )
            if p_topic and p_topic.get("status") != "studied":
                missing_prereqs[p_topic["topic"]] = p_topic

    if not missing_prereqs:
        print("    (None)")
    else:
        for p in sorted(
            missing_prereqs.values(), key=lambda x: x.get("playlist_day", 999)
        ):
            print(
                f"    [NO] Day {p.get('playlist_day', '?')} — {p['topic']:<30} [{p.get('status', 'not_started')}]"
            )

    print("\n    TEXTBOOK CHAPTERS TO READ FOR THIS BATCH:")
    books = {}
    book_days = {}
    for t in selected_topics:
        day = t.get("playlist_day")
        for s in t.get("textbook_sources", []):
            book = s["book"]
            if book not in books:
                books[book] = set()
                book_days[book] = set()
            for c in s.get("chapters", []):
                books[book].add(str(c))
            if day:
                book_days[book].add(day)

    if not books:
        print("    (No textbook readings mapped for this batch)")
    else:
        for book in sorted(books.keys()):
            ch_str = ", ".join(
                sorted(
                    list(books[book]),
                    key=lambda x: float(x) if x.replace(".", "", 1).isdigit() else 999,
                )
            )
            days_set = sorted(list(book_days[book]))
            if len(days_set) == 1:
                cov_str = f"covers Day {days_set[0]} only"
            elif (
                len(days_set) > 1 and len(days_set) == max(days_set) - min(days_set) + 1
            ):
                cov_str = f"covers Days {min(days_set)}–{max(days_set)}"
            else:
                cov_str = f"covers Days {', '.join(map(str, days_set))}"
            print(f"    {book:<5} Chapter {ch_str:<10} ({cov_str})")

        print("\n    Chapters are deduplicated — read each chapter once")
        print("    for the whole batch, not once per topic.")

    print(f"\n  {'═' * 56}\n")


# ── CLI ────────────────────────────────────────────────────────────────────────


def parse_day_arg(arg: str) -> list:
    """Parses '57', '57-62', '50,51,52' into a list of ints."""
    days = []
    for part in arg.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-")
            days.extend(range(int(a), int(b) + 1))
        else:
            days.append(int(part))
    return days


def main():
    parser = argparse.ArgumentParser(
        description="Generate Obsidian ML notes from textbooks"
    )
    parser.add_argument("--day", type=int, help="Single day number")
    parser.add_argument("--days", type=str, help="Range or list: '57-62' or '50,51,52'")
    parser.add_argument("--section", type=str, help="All topics in a named section")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without API calls or file writes",
    )
    parser.add_argument(
        "--brief", action="store_true", help="View study summary without generating"
    )
    args = parser.parse_args()

    if args.dry_run and args.brief:
        parser.error(
            "Cannot use --dry-run and --brief together. They are mutually exclusive."
        )

    all_topics = load_topics()
    formulas = load_formulas()
    mappings = load_mappings()

    if args.day:
        selected = [t for t in all_topics if t.get("playlist_day") == args.day]
    elif args.days:
        day_list = parse_day_arg(args.days)
        selected = [t for t in all_topics if t.get("playlist_day") in day_list]
    elif args.section:
        selected = [
            t
            for t in all_topics
            if t.get("section", "").lower() == args.section.lower()
        ]
    else:
        parser.print_help()
        print("\n  ERROR: specify --day, --days, or --section")
        print("  Examples:")
        print("    python scripts/generate_notes.py --day 57")
        print("    python scripts/generate_notes.py --days 57-62")
        print("    python scripts/generate_notes.py --section 'Linear Regression'")
        print("    python scripts/generate_notes.py --days 50-52 --dry-run")
        return

    if not selected:
        print("  No topics matched. Check day numbers or section name.")
        return

    if args.brief:
        print(f"\n[BRIEF MODE] Generating summaries for {len(selected)} topic(s)...\n")
        seen_groups = set()
        for topic in selected:
            grp = topic.get("merge_group")
            if grp:
                if grp not in seen_groups:
                    group_topics = sorted(
                        [t for t in all_topics if t.get("merge_group") == grp],
                        key=lambda x: x["playlist_day"],
                    )
                    vault_path = get_vault_path_merged(group_topics[0], grp)
                    print_group_summary(
                        grp,
                        group_topics,
                        all_topics,
                        formulas,
                        mappings,
                        vault_path,
                        is_brief=True,
                    )
                    seen_groups.add(grp)
            else:
                print_topic_summary(
                    topic, all_topics, formulas, mappings, is_brief=True
                )

        if len(selected) > 1 or args.days or args.section:
            print_batch_summary(selected, all_topics, is_brief=True)
        return

    mode = "[DRY RUN] " if args.dry_run else ""
    print(f"\n{mode}Generating {len(selected)} note(s)...\n")

    success = failed = 0
    for topic in selected:
        ok = generate_note(topic, all_topics, formulas, mappings, dry_run=args.dry_run)
        if ok:
            success += 1
        else:
            failed += 1

    if not args.dry_run and (len(selected) > 1 or args.days or args.section):
        print_batch_summary(
            selected, all_topics, is_brief=False, generated_count=success
        )

    print(f"\n{'=' * 50}")
    print(f"  {'[DRY RUN] ' if args.dry_run else ''}Complete")
    print(f"  [OK] Success: {success}")
    if failed:
        print(f"  [FAILED] Failed:  {failed} — see failed_topics.json")
    print(f"{'=' * 50}\n")


if __name__ == "__main__":
    main()
