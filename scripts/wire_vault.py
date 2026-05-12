import argparse
import json
import re
from pathlib import Path

TOPICS_FILE = Path("topics.json")
FORMULAS_FILE = Path("formulas.json")

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

def load_json(path: Path):
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_vault_path(topic: dict) -> Path:
    section = topic.get("section", "Foundations")
    safe_section = section.replace(" (Unsupervised Learning)", "").replace(" ", "_")
    folder  = f"KB_Obsidian/{safe_section}/"
    slug    = (topic["topic"].lower()
               .replace(" ", "_")
               .replace("-", "_")
               .replace("/", "_"))
    day = topic.get("playlist_day", "X")
    return Path(folder) / f"day_{day}_{slug}.md"

def get_topic_by_name(name: str, all_topics: list) -> dict:
    for t in all_topics:
        if t["topic"].lower() == name.lower():
            return t
    return None

def compute_unlocks(topic_name: str, all_topics: list) -> list:
    unlocks = []
    for t in all_topics:
        if any(p.lower() == topic_name.lower() for p in t.get("prerequisites", [])):
            unlocks.append(t)
    # Sort by day and take max 6
    unlocks.sort(key=lambda x: x.get("playlist_day", 999))
    return unlocks[:6]

def compute_same_section(topic: dict, all_topics: list) -> list:
    section_topics = [
        t for t in all_topics 
        if t.get("section") == topic.get("section") and t["topic"] != topic["topic"]
    ]
    section_topics.sort(key=lambda x: x.get("playlist_day", 999))
    return section_topics[:5]

def compute_see_also(topic: dict, all_topics: list) -> list:
    see_also = []
    my_books = {s["book"] for s in topic.get("textbook_sources", [])}
    if not my_books:
        return []
        
    for t in all_topics:
        if t["topic"] == topic["topic"] or t.get("section") == topic.get("section"):
            continue
        their_books = {s["book"] for s in t.get("textbook_sources", [])}
        if my_books.intersection(their_books):
            see_also.append(t)
            
    # Sort by day or relevance
    see_also.sort(key=lambda x: x.get("playlist_day", 999))
    return see_also[:4]

def wire_note(topic: dict, all_topics: list, dry_run: bool):
    file_path = get_vault_path(topic)
    
    if not file_path.exists():
        # Fallback check just in case it doesn't have the day prefix
        safe_section = topic.get("section", "Foundations").replace(" (Unsupervised Learning)", "").replace(" ", "_")
        slug = (topic["topic"].lower().replace(" ", "_").replace("-", "_").replace("/", "_"))
        fallback_path = Path(f"KB_Obsidian/{safe_section}/{slug}.md")
        if fallback_path.exists():
            file_path = fallback_path
        else:
            return False, "Not generated yet"

    content = file_path.read_text(encoding="utf-8")
    original_content = content
    
    # 1. Add YAML Frontmatter if missing
    if not content.startswith("---"):
        tags = [
            topic.get("section", "Misc").replace(" ", ""),
            topic.get("difficulty", "medium"),
            classify_topic(topic)
        ]
        
        prereqs_list = topic.get("prerequisites", [])
        prereqs_formatted = "[" + ", ".join([f'"[[{p}]]"' for p in prereqs_list]) + "]" if prereqs_list else "[]"
        tags_formatted = "[" + ", ".join([f'"{t}"' for t in tags]) + "]"
        
        frontmatter = (
            "---\n"
            f"topic: \"{topic['topic']}\"\n"
            f"section: \"{topic.get('section', '')}\"\n"
            f"playlist_day: {topic.get('playlist_day', 'null')}\n"
            f"difficulty: \"{topic.get('difficulty', 'medium')}\"\n"
            f"interview_importance: {topic.get('interview_importance') or 'null'}\n"
            f"status: \"{topic.get('status', 'not_started')}\"\n"
            f"tags: {tags_formatted}\n"
            f"prerequisites: {prereqs_formatted}\n"
            "---\n\n"
        )
        content = frontmatter + content

    # 2. Replace the bottom section with Structured Links
    # The generation script outputs: "--- \n Prerequisites: [[link]]" at the bottom
    # We will look for everything from the last "---" onwards that includes "Prerequisites:"
    
    links_marker = "\n---\nPrerequisites:"
    if links_marker in content:
        # Split at the exact generation marker
        main_body, _ = content.rsplit(links_marker, 1)
        
        # Build structured links block
        links_block = "\n---\n## Links\n\n"
        
        # Prerequisites
        prereqs = topic.get("prerequisites", [])
        if prereqs:
            links_block += "**Prerequisites**\n"
            for p in prereqs:
                links_block += f"- [[{p}]]\n"
            links_block += "\n"
            
        # Unlocks
        unlocks = compute_unlocks(topic["topic"], all_topics)
        if unlocks:
            links_block += "**Unlocks**\n"
            for u in unlocks:
                links_block += f"- [[{u['topic']}]]\n"
            links_block += "\n"
            
        # Same Section
        same_sec = compute_same_section(topic, all_topics)
        if same_sec:
            links_block += "**Same Section**\n"
            for s in same_sec:
                links_block += f"- [[{s['topic']}]]\n"
            links_block += "\n"
            
        # See Also
        see_also = compute_see_also(topic, all_topics)
        if see_also:
            links_block += "**See Also**\n"
            for s in see_also:
                links_block += f"- [[{s['topic']}]]\n"
            links_block += "\n"
            
        content = main_body + links_block
        
    if content != original_content:
        if not dry_run:
            file_path.write_text(content, encoding="utf-8")
        return True, "Wired frontmatter and links"
    
    return False, "Already wired or generation marker not found"

def generate_moc(section: str, all_topics: list, formulas: list, dry_run: bool):
    safe_section = section.replace(" (Unsupervised Learning)", "").replace(" ", "_")
    folder = Path(f"KB_Obsidian/{safe_section}")
    folder.mkdir(parents=True, exist_ok=True)
    moc_path = folder / f"🗺 {section} MOC.md"
    
    section_topics = [t for t in all_topics if t.get("section") == section]
    if not section_topics:
        return False, "No topics in section"
        
    section_topics.sort(key=lambda x: x.get("playlist_day", 999))
    
    # 1. Table of Topics
    table = "| Day | Topic | Difficulty | Interview Importance | Status |\n"
    table += "|---|---|---|---|---|\n"
    for t in section_topics:
        day = t.get("playlist_day", "-")
        imp = t.get("interview_importance") or "-"
        table += f"| {day} | [[{t['topic']}]] | {t.get('difficulty', '-')} | {imp} | {t.get('status', '-')} |\n"
        
    # 2. Dependency Graph
    graph = ""
    for t in section_topics:
        prereqs = t.get("prerequisites", [])
        if prereqs:
            for p in prereqs:
                graph += f"[[{p}]] → [[{t['topic']}]]\n"
    if not graph:
        graph = "No strict dependencies defined in this section.\n"
        
    # 3. Key Formulas
    formula_list = ""
    topic_names = {t["topic"].lower() for t in section_topics}
    topic_slugs = {t["topic"].lower().replace(" ", "_").replace("-", "_").replace("/", "_") for t in section_topics}
    for f in formulas:
        if f.get("topic") in topic_slugs or f.get("section") == section:
            formula_list += f"- **{f.get('name', 'Formula')}**: {f.get('latex', '')}\n"
    if not formula_list:
        formula_list = "(No extracted formulas for this section)\n"
        
    # 4. Ranked Revision
    ranked = sorted(
        [t for t in section_topics if t.get("interview_importance")], 
        key=lambda x: x["interview_importance"], 
        reverse=True
    )
    revision_list = ""
    for i, t in enumerate(ranked):
        revision_list += f"{i+1}. [[{t['topic']}]] ({t['interview_importance']}/10)\n"
    if not revision_list:
        revision_list = "No topics with interview importance ratings in this section.\n"
        
    # 5. Textbook Readings
    books = {}
    for t in section_topics:
        for s in t.get("textbook_sources", []):
            b = s["book"]
            for c in s.get("chapters", []):
                if b not in books:
                    books[b] = set()
                books[b].add(str(c))
                
    reading_list = ""
    for b, chs in books.items():
        reading_list += f"**{b}**\n"
        for c in sorted(list(chs), key=lambda x: float(x) if x.replace('.', '', 1).isdigit() else 999):
            reading_list += f"- Chapter {c}\n"
    if not reading_list:
        reading_list = "No textbooks mapped for this section.\n"
        
    moc_content = f"""# {section} MOC

## Topics
{table}

## Dependency Graph
{graph}

## Key Formulas
{formula_list}

## Ranked Revision
{revision_list}

## Textbook Readings
{reading_list}
"""
    
    if not dry_run:
        moc_path.write_text(moc_content, encoding="utf-8")
    return True, "Generated MOC"

def main():
    parser = argparse.ArgumentParser(description="Wire Obsidian Vault Notes")
    parser.add_argument("--section", type=str, help="Process specific section only")
    parser.add_argument("--all", action="store_true", help="Process entire vault")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without writing")
    args = parser.parse_args()
    
    if not args.section and not args.all:
        parser.error("Must specify either --section or --all")
        
    all_topics = load_json(TOPICS_FILE)
    formulas = load_json(FORMULAS_FILE)
    
    if not all_topics:
        print("Error: Could not load topics.json")
        return
        
    mode = "[DRY RUN] " if args.dry_run else ""
    print(f"\n{mode}Starting Vault Wiring...\n")
    
    if args.section:
        target_topics = [t for t in all_topics if t.get("section", "").lower() == args.section.lower()]
        target_sections = {target_topics[0]["section"]} if target_topics else set()
    else:
        target_topics = all_topics
        target_sections = {t.get("section") for t in all_topics if t.get("section")}
        
    if not target_topics:
        print("No matching topics found.")
        return
        
    print("--- Wiring Notes ---")
    wired_count = 0
    for t in target_topics:
        changed, msg = wire_note(t, all_topics, args.dry_run)
        if changed:
            print(f"  [OK] {t['topic']} -> {msg}")
            wired_count += 1
        else:
            if msg != "Not generated yet":
                print(f"  [SKIP] {t['topic']} -> {msg}")
            
    print(f"\nTotal notes wired: {wired_count}")
    
    print("\n--- Generating MOCs ---")
    for sec in target_sections:
        changed, msg = generate_moc(sec, all_topics, formulas, args.dry_run)
        if changed:
            print(f"  [OK] {sec} -> {msg}")

if __name__ == "__main__":
    main()
