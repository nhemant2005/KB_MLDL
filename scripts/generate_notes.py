import anthropic
import argparse
import fitz
import json
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

client = anthropic.Anthropic()

BOOK_PATHS = {
    "HOML": "Textbooks/[2] Aurélien Géron - Hands-On Machine Learning with Scikit-Learn, Keras, and Tensorflow_ Concepts, Tools, and Techniques to Build Intelligent System (2019, O’Reilly Media) - libgen.li.pdf",
    "ISL":  "Textbooks/[Springer Texts in Statistics] Gareth James, Daniela Witten, Trevor Hastie, Robert Tibshirani - An Introduction to Statistical Learning - with Applications in R (2021, Springer Science+Business Media) - libgen.li.pdf",
    "PRML": "Textbooks/[Information Science and Statistics ] Christopher M. Bishop - Pattern Recognition and Machine Learning (2006, Springer) - libgen.li.pdf"
}

# Filled after TOC inspection and my confirmation
CHAPTER_PAGE_MAP = {
    'HOML': {
        '1': (19, 59), '2': (60, 120), '3': (121, 153), '4': (154, 203),
        '5': (204, 228), '6': (229, 243), '7': (244, 272), '8': (273, 298),
        '9': (299, 348), '11': (414, 465), '12': (466, 510)
    },
    'ISL': {
        '1': (16, 29), '2': (30, 72), '3': (73, 142), '4': (143, 209),
        '5': (210, 236), '6': (237, 300), '7': (301, 338), '8': (339, 377),
        '9': (378, 413), '12': (507, 562)
    },
    'PRML': {
        '1': (21, 86), '2': (87, 156), '3': (157, 198), '4': (199, 244),
        '5': (245, 310), '6': (311, 344), '7': (345, 378), '12': (579, 624),
        '14': (673, 696)
    }
}

# VAULT_SECTION_MAP is now handled dynamically in get_vault_path 
# to perfectly mirror the sections defined in mapping.txt

# ── TOPIC TYPE CLASSIFICATION ──────────────────────────────────────────────────
# Controls which note template is used.
# Edit these sets after reviewing your topics.json if needed.

TOOLING_TOPICS = {
    "installing_anaconda", "working_with_csv_files",
    "working_with_json_sql", "fetching_data_from_an_api",
    "web_scraping", "pandas_profiling", "column_transformer",
    "ml_pipelines", "decision_tree_visualization",
    "hyperparameter_tuning_rf_using_gridsearchcv",
    "xgboost_for_regression", "xgboost_for_classification",
    "naive_bayes_code_example", "end_to_end_toy_project",
    "knn_code", "svm_kernel_code_example"
}

MATH_FOUNDATION_TOPICS = {
    "what_are_tensors", "curse_of_dimensionality",
    "derivative_of_sigmoid", "why_lasso_creates_sparsity",
    "the_maths_behind_xgboost",
    "gradient_boosting_regression_mathematics",
    "ridge_regression_mathematical_formulation",
    "multiple_linear_regression_mathematical_formulation",
    "simple_linear_regression_mathematical_formulation",
    "naive_bayes_mathematics", "svm_hard_margin_mathematics",
    "svm_soft_margin_mathematics",
    "pca_mathematical_formulation"
}

def classify_topic(topic: dict) -> str:
    """
    Returns one of four note types:
      'tooling'     → cheatsheet style, code-heavy, minimal math
      'math_heavy'  → full derivation, every step shown
      'algorithm'   → intuition + math + interview prep (scaled by importance)
      'concept'     → explanation-focused, light math
    """
    slug = (topic["topic"].lower()
            .replace(" ", "_")
            .replace("-", "_")
            .replace("/", "_"))
    if slug in TOOLING_TOPICS:
        return "tooling"
    if slug in MATH_FOUNDATION_TOPICS:
        return "math_heavy"
    if topic.get("difficulty") in ("high", "medium"):
        return "algorithm"
    return "concept"


# ── TEXTBOOK EXTRACTION ────────────────────────────────────────────────────────

def extract_chapter_cached(book: str, chapter: int) -> str:
    cache_path = Path(
        f"textbooks/extracted/{book.lower()}_ch{chapter}.txt"
    )
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
        book     = source["book"]
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
                f"{'='*60}\n"
                f"SOURCE: {book} | Chapter {chapter} "
                f"| Priority: {priority.upper()}\n"
                f"{'='*60}\n"
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
    note_type  = classify_topic(topic)
    prereqs    = topic.get("prerequisites", [])
    prereq_links = " ".join([f"[[{p}]]" for p in prereqs])
    importance = topic.get("interview_importance", 5)
    difficulty = topic.get("difficulty", "medium")

    # ── Shared rules header ────────────────────────────────────
    header = f"""You are generating an Obsidian markdown companion note
for the CampusX 100 Days of ML playlist and its mapped textbooks.

This note serves two purposes simultaneously:
  1. A companion to the playlist video for Day {topic['playlist_day']}
  2. A companion to the textbook sections listed as sources

Topic: {topic['topic']}
Section: {topic['section']}
Playlist Day: {topic['playlist_day']}
Difficulty: {difficulty}
Interview Importance: {importance}/10
Note Type: {note_type}
Prerequisites: {prereqs}

NON-NEGOTIABLE RULES:
- Use ONLY the textbook content provided at the bottom of this prompt
- Do NOT use your training data or memory for any fact or formula
- Every non-trivial claim must end with its source in parentheses:
    (HOML ch.4) or (ISL ch.3) or (PRML ch.7)
- All mathematics must be LaTeX: $inline$ or $$block$$
- [[backlinks]] must use ONLY exact topic names from the
  prerequisites list above — do not invent new backlinks
- If textbook content is missing or insufficient for any section,
  write exactly:
    > [NEEDS REVIEW: insufficient source material]
  Do NOT fill gaps from memory.
- Output ONLY the markdown note. No preamble. No explanation.
- Respect the word limits specified in the template below.
"""

    # ── Template: TOOLING ──────────────────────────────────────
    if note_type == "tooling":
        template = f"""
Generate a TOOLING COMPANION NOTE.
This is a practical reference cheatsheet, not a theory note.
Total length: 300–450 words maximum.

# {topic['topic']}

## What It Does
1–2 sentences only. What is this tool or function for?
Cite textbook source.

## When To Use It
Bullet list. 3–4 practical scenarios.

## Core Syntax / API
Code block showing the most important usage patterns.
Comment every parameter that matters.
Pull examples directly from textbook if available.

## Key Parameters
Bullet list or small table.
  Parameter | what it controls | typical value
Only parameters the textbook explicitly covers.

## Common Mistakes
Bullet list. 3 points maximum.
What breaks in practice.

## Textbook Coverage
One sentence: what the textbook covers here and what it skips.
Be honest if coverage is shallow.

## Related Topics
Maximum 3. Use [[backlinks]] for prerequisites only.

---
Prerequisites: {prereq_links}
"""

    # ── Template: MATH_HEAVY ───────────────────────────────────
    elif note_type == "math_heavy":
        template = f"""
Generate a MATHEMATICAL DERIVATION NOTE.
This note exists solely to show the full mathematical argument.
Total length: 500–700 words.

# {topic['topic']}

## Why This Math Matters
2–3 sentences. What does this derivation prove or enable?
Interview importance is {importance}/10 — reflect this in depth.

## Prerequisites Assumed
Bullet list. What must the reader already know?
Draw only from: {prereqs}

## Full Derivation
Show every step. Number each step.
Explain what is happening at each transition in plain English.
If the textbook skips steps, note it explicitly:
  > [Textbook skips from step X to Y — intermediate step shown]
Do NOT skip steps yourself.
Source every equation: (HOML ch.4) or (PRML ch.3)

## Key Result
State the final formula in a LaTeX block.
One sentence: what does this result mean geometrically
or statistically?

## Intuition Behind The Math
2–3 sentences. Plain English restatement of the derivation.
What is the math actually doing?

## Where This Formula Appears
Bullet list. Which algorithms use this result directly?
Maximum 4 items. Use [[backlinks]] where applicable.

## Interview Angle
2–3 sentences. How is this derivation tested in interviews?
What level of depth is expected at {importance}/10 importance?

---
Prerequisites: {prereq_links}
"""

    # ── Template: ALGORITHM ────────────────────────────────────
    elif note_type == "algorithm":

        if importance >= 9:
            math_block = """## Mathematical Formulation
Full derivation required. Show all steps with numbered transitions.
Explain each step in plain English alongside the math.
Source every equation."""
            interview_block = "5 questions. Mix of conceptual and derivation-level. Order most-to-least common."
            word_limit = "600–800 words"

        elif importance >= 7:
            math_block = """## Mathematical Formulation
Key equations with explanation of each term.
Intuition for why the math is structured this way.
No need for full derivation unless the textbook provides it explicitly."""
            interview_block = "4 questions. Mostly conceptual with one math question."
            word_limit = "450–600 words"

        else:
            math_block = """## Mathematical Formulation
Core equation only. One sentence explanation of each term.
Skip derivation entirely."""
            interview_block = "3 questions. Conceptual only."
            word_limit = "350–500 words"

        template = f"""
Generate an ALGORITHM COMPANION NOTE.
Total length: {word_limit}.

# {topic['topic']}

## Core Idea
2–3 sentences. Plain English.
What problem does this algorithm solve?
Why does it exist — what gap does it fill?

## Intuition
3–5 sentences. Build intuition before math.
Use the textbook's own explanations and examples.
Cite source for every claim.

{math_block}

## Key Formulas
Bullet list. LaTeX. One formula per bullet.
Name each formula. Source each formula.
Only formulas the textbook explicitly states — do not add others.

## Assumptions
Bullet list.
When does this algorithm assume something about the data?
Pull directly from textbook — do not invent assumptions.

## Step-by-Step Algorithm
Numbered list. Maximum 7 steps.
Follow the textbook's own description of the algorithm.

## Hyperparameters
Bullet list or small table.
  Parameter | effect on model | how to tune
Only cover what the textbook discusses.

## Failure Modes
Bullet list.
When does this break?
What does the textbook specifically warn about?

## Interview Questions
{interview_block}
Questions only — no answers in this section.

## Code Example
Minimal sklearn or numpy snippet.
Comment every non-obvious line.
Follow textbook's own code examples where available.

## Related Topics
Bullet list. Maximum 5.
[[backlinks]] for prerequisites only.
Plain text for related topics not in prerequisites.

---
Prerequisites: {prereq_links}
"""

    # ── Template: CONCEPT ──────────────────────────────────────
    else:
        template = f"""
Generate a CONCEPT EXPLANATION NOTE.
Total length: 300–450 words maximum.

# {topic['topic']}

## Core Idea
2–3 sentences. Plain English. What is this concept?

## Why It Matters
2–3 sentences.
Why does an ML practitioner need to understand this?
Tie to downstream algorithms where possible.

## Explanation
3–5 sentences expanding the core idea.
Use the textbook's own explanation and examples.
Cite source for every claim.

## Key Terms
Bullet list.
  Term: one-line definition
Only terms the textbook explicitly defines in this context.

## Common Misunderstanding
1–2 sentences.
What do beginners typically get wrong about this concept?

## Interview Relevance
1–2 sentences.
How does this concept appear in interviews?
Interview importance is {importance}/10 — reflect this honestly.

## Related Topics
Maximum 4.
[[backlinks]] for prerequisites only.

---
Prerequisites: {prereq_links}
"""

    # ── Assemble ───────────────────────────────────────────────
    return (
        header
        + "\n"
        + template
        + f"\n\n{'='*60}\n"
        + "TEXTBOOK CONTENT — USE ONLY THIS AS YOUR SOURCE:\n"
        + f"{'='*60}\n\n"
        + textbook_content
    )


# ── VAULT PATH ─────────────────────────────────────────────────────────────────

def get_vault_path(topic: dict) -> Path:
    section = topic.get("section", "Foundations")
    # Clean section name to make a nice directory name
    safe_section = section.replace(" (Unsupervised Learning)", "").replace(" ", "_")
    folder  = f"KB_Obsidian/{safe_section}/"
    slug    = (topic["topic"].lower()
               .replace(" ", "_")
               .replace("-", "_")
               .replace("/", "_"))
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
    path     = Path("failed_topics.json")
    failures = []
    if path.exists():
        with open(path) as f:
            failures = json.load(f)
    failures.append({
        "topic": topic["topic"],
        "day":   topic["playlist_day"],
        "error": error
    })
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

def generate_note(topic: dict, all_topics: list, formulas: list, mappings: dict, dry_run: bool = False) -> bool:
    progress  = load_progress()
    topic_key = f"day_{topic['playlist_day']}"

    if progress.get(topic_key) == "done":
        print(f"  [skip] Day {topic['playlist_day']}: "
              f"{topic['topic']} — already generated")
        print_topic_summary(topic, all_topics, formulas, mappings, is_brief=False)
        return True

    textbook_content = build_textbook_content(topic)
    vault_path       = get_vault_path(topic)

    if dry_run:
        sources = [
            f"{s['book']} ch.{c}"
            for s in topic.get("textbook_sources", [])
            for c in s.get("chapters", [])
        ]
        has_content = (
            "YES" if "EXTRACTION FAILED" not in textbook_content
                     and "CRITICAL" not in textbook_content
                     and textbook_content.strip()
            else "NO — run extract_textbook_sections.py first"
        )
        print(f"\n  [dry-run] Day {topic['playlist_day']}: "
              f"{topic['topic']}")
        print(f"    Note type:   {classify_topic(topic)}")
        print(f"    Section:     {topic['section']}")
        print(f"    Difficulty:  {topic['difficulty']}")
        print(f"    Importance:  {topic.get('interview_importance')}/10")
        print(f"    Sources:     {', '.join(sources) or 'none mapped'}")
        print(f"    Output:      {vault_path}")
        print(f"    Content:     {has_content}")
        return True

    print(f"\n  Generating: Day {topic['playlist_day']} — "
          f"{topic['topic']} [{classify_topic(topic)}]")

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": build_prompt(topic, textbook_content)
            }]
        )
        note_content = response.content[0].text

        vault_path.parent.mkdir(parents=True, exist_ok=True)
        vault_path.write_text(note_content, encoding="utf-8")

        progress[topic_key] = "done"
        save_progress(progress)

        print(f"  [OK] Saved -> {vault_path}")
        print_topic_summary(topic, all_topics, formulas, mappings, is_brief=False)
        time.sleep(2)  # API rate limit safety
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

def print_topic_summary(topic: dict, all_topics: list, formulas: list, mappings: dict, is_brief: bool = False):
    vault_path = get_vault_path(topic)
    day = topic.get('playlist_day', '?')
    
    print(f"\n  {'='*56}")
    print(f"    DAY {day} — {topic['topic']}")
    print(f"    Section: {topic.get('section', '-')}  |  Difficulty: {topic.get('difficulty', 'medium')}")
    print(f"    Interview Importance: {topic.get('interview_importance') or '-'}/10")
    print(f"  {'='*56}\n")
    
    # 1. PREREQUISITES
    print("    PREREQUISITES — study these first if not done:")
    print("    ---------------------------------------------")
    prereqs = topic.get("prerequisites", [])
    if not prereqs:
        print("    [OK] No prerequisites for this topic")
    else:
        all_met = True
        for p_name in prereqs:
            p_topic = next((t for t in all_topics if t["topic"].lower() == p_name.lower()), None)
            if p_topic:
                status = p_topic.get("status", "not_started")
                p_day = p_topic.get("playlist_day", "?")
                if status == "studied":
                    print(f"    [OK] Day {p_day} — {p_topic['topic']} [studied]")
                else:
                    print(f"    [NO] Day {p_day} — {p_topic['topic']} [{status}]  <- do this first")
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
                        wrapped = textwrap.fill(f"-> Topic maps to: {mapping_text}", width=45, subsequent_indent="          ")
                        for line in wrapped.split('\n'):
                            print(f"        {line.strip()}")
                        print("")
        
        if not any(s["book"] == "PRML" for s in sources):
            print("\n    (No PRML reference for this topic)")

    # 3. KEY FORMULAS
    print("\n    KEY FORMULAS FOR THIS TOPIC:")
    print("    ---------------------------------------------")
    topic_slug = topic["topic"].lower().replace(" ", "_").replace("-", "_").replace("/", "_")
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
            print(f"    Note type:    {classify_topic(topic)}")
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
            rel_path_str = vault_path.relative_to(vault_path.parts[0]).with_suffix("").as_posix()
        except ValueError:
            rel_path_str = vault_path.with_suffix("").as_posix()
        print(f"    obsidian://open?vault={vault_path.parts[0]}&file={rel_path_str}")
        
    print(f"\n  {'='*56}\n")

def print_batch_summary(selected_topics: list, all_topics: list, is_brief: bool, generated_count: int = 0):
    if not selected_topics:
        return
        
    days = [t.get("playlist_day") for t in selected_topics if t.get("playlist_day")]
    if not days:
        return
    min_day, max_day = min(days), max(days)
    day_str = f"Day {min_day}" if min_day == max_day else f"Days {min_day}-{max_day}"
    section = selected_topics[0].get("section", "Misc")
    
    print(f"\n  {'='*56}")
    print(f"    BATCH COMPLETE — {day_str} ({section})")
    print(f"  {'='*56}\n")
    
    total = len(selected_topics)
    
    if is_brief:
        existing = sum(1 for t in selected_topics if get_vault_path(t).exists())
        print(f"    Notes already generated:  {existing} / {total}")
        missing = total - existing
        if missing > 0:
            missing_days = [str(t.get("playlist_day")) for t in selected_topics if not get_vault_path(t).exists()]
            print(f"    Notes not yet generated:  {missing} / {total}  (Days {', '.join(missing_days)})")
    else:
        print(f"    Notes generated: {generated_count}")
        print(f"    Failed:          {total - generated_count}")
        
    print("\n    PREREQUISITES NOT YET STUDIED ACROSS THIS BATCH:")
    missing_prereqs = {}
    for t in selected_topics:
        for p_name in t.get("prerequisites", []):
            p_topic = next((tp for tp in all_topics if tp["topic"].lower() == p_name.lower()), None)
            if p_topic and p_topic.get("status") != "studied":
                missing_prereqs[p_topic["topic"]] = p_topic
                
    if not missing_prereqs:
        print("    (None)")
    else:
        for p in sorted(missing_prereqs.values(), key=lambda x: x.get("playlist_day", 999)):
            print(f"    [NO] Day {p.get('playlist_day', '?')} — {p['topic']:<30} [{p.get('status', 'not_started')}]")

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
            ch_str = ", ".join(sorted(list(books[book]), key=lambda x: float(x) if x.replace('.', '', 1).isdigit() else 999))
            days_set = sorted(list(book_days[book]))
            if len(days_set) == 1:
                cov_str = f"covers Day {days_set[0]} only"
            elif len(days_set) > 1 and len(days_set) == max(days_set) - min(days_set) + 1:
                cov_str = f"covers Days {min(days_set)}–{max(days_set)}"
            else:
                cov_str = f"covers Days {', '.join(map(str, days_set))}"
            print(f"    {book:<5} Chapter {ch_str:<10} ({cov_str})")
            
        print("\n    Chapters are deduplicated — read each chapter once")
        print("    for the whole batch, not once per topic.")
        
    print(f"\n  {'═'*56}\n")


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
    parser.add_argument("--day",     type=int, help="Single day number")
    parser.add_argument("--days",    type=str,
                        help="Range or list: '57-62' or '50,51,52'")
    parser.add_argument("--section", type=str,
                        help="All topics in a named section")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without API calls or file writes")
    parser.add_argument("--brief", action="store_true",
                        help="View study summary without generating")
    args = parser.parse_args()

    if args.dry_run and args.brief:
        parser.error("Cannot use --dry-run and --brief together. They are mutually exclusive.")

    all_topics = load_topics()
    formulas = load_formulas()
    mappings = load_mappings()

    if args.day:
        selected = [t for t in all_topics
                    if t.get("playlist_day") == args.day]
    elif args.days:
        day_list = parse_day_arg(args.days)
        selected = [t for t in all_topics
                    if t.get("playlist_day") in day_list]
    elif args.section:
        selected = [t for t in all_topics
                    if t.get("section", "").lower() == args.section.lower()]
    else:
        parser.print_help()
        print("\n  ERROR: specify --day, --days, or --section")
        print("  Examples:")
        print("    python scripts/generate_notes.py --day 57")
        print("    python scripts/generate_notes.py --days 57-62")
        print("    python scripts/generate_notes.py "
              "--section 'Linear Regression'")
        print("    python scripts/generate_notes.py "
              "--days 50-52 --dry-run")
        return

    if not selected:
        print("  No topics matched. Check day numbers or section name.")
        return

    if args.brief:
        print(f"\n[BRIEF MODE] Generating summaries for {len(selected)} topic(s)...\n")
        for topic in selected:
            print_topic_summary(topic, all_topics, formulas, mappings, is_brief=True)
        
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
        print_batch_summary(selected, all_topics, is_brief=False, generated_count=success)

    print(f"\n{'='*50}")
    print(f"  {'[DRY RUN] ' if args.dry_run else ''}Complete")
    print(f"  [OK] Success: {success}")
    if failed:
        print(f"  [FAILED] Failed:  {failed} — see failed_topics.json")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    main()
