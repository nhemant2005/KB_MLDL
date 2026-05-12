import json
import re
from pathlib import Path

VAULT_DIR = Path("KB_Obsidian")
OUTPUT_FILE = Path("formulas.json")
TOPICS_FILE = Path("topics.json")

def load_topics_metadata() -> dict:
    if not TOPICS_FILE.exists():
        return {}
    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        topics = json.load(f)
        
    metadata = {}
    for t in topics:
        # Create a matching key based on the topic name to map back from markdown filename
        slug = t["slug"]
        metadata[slug] = t
    return metadata

def extract_formulas_from_note(file_path: Path, metadata: dict) -> list:
    content = file_path.read_text(encoding="utf-8")
    formulas = []
    
    topic_slug = file_path.stem
    topic_meta = metadata.get(topic_slug, {})
    
    section_name = topic_meta.get("section", file_path.parent.name)
    difficulty = topic_meta.get("difficulty", "medium")
    interview_importance = topic_meta.get("interview_importance", 5)
    
    derivation_required = bool(interview_importance >= 9 and difficulty == "high")
    
    # Extract ## Key Formulas section
    formulas_section = re.search(r"## Key Formulas\n(.*?)(?=\n## |\Z)", content, re.DOTALL)
    
    if not formulas_section:
        return []
        
    formula_lines = formulas_section.group(1).strip().split('\n')
    
    for idx, line in enumerate(formula_lines):
        line = line.strip()
        if not line or not line.startswith('-'):
            continue
            
        latex_match = re.search(r"(\$\$[^\$]+\$\$|\$[^\$]+\$)", line)
        if latex_match:
            latex = latex_match.group(1)
            name_text = line.replace(latex, "").replace('- ', '').strip(' :*')
            
            formula_id = f"{topic_slug}_formula_{idx+1}"
            
            formulas.append({
                "formula_id": formula_id,
                "latex": latex,
                "name": name_text if name_text else "Formula",
                "meaning": "Meaning extracted from note context",
                "topic": topic_slug,
                "section": section_name,
                "interview_importance": interview_importance,
                "derivation_required": derivation_required
            })
            
    return formulas

def main():
    if not VAULT_DIR.exists():
        print(f"Vault directory '{VAULT_DIR}' not found. Cannot extract formulas until notes are generated.")
        return
        
    metadata = load_topics_metadata()
    all_formulas = []
    
    for md_file in VAULT_DIR.rglob("*.md"):
        formulas = extract_formulas_from_note(md_file, metadata)
        all_formulas.extend(formulas)
        
    print(f"\nExtracted {len(all_formulas)} total formulas.")
    
    if not all_formulas:
        print("No formulas found.")
        return
        
    # Preview the first 5 formulas
    print("\n--- PREVIEW OF FIRST 5 FORMULAS ---")
    for f in all_formulas[:5]:
        print(json.dumps(f, indent=2))
        
    print("\n[Preview Complete]")
    
    # Prompt for approval
    ans = input("Do you approve saving these formulas to formulas.json? (y/n): ")
    if ans.lower().strip() == 'y':
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(all_formulas, f, indent=2)
        print(f"Formulas saved to {OUTPUT_FILE}")
    else:
        print("Operation cancelled. formulas.json was not updated.")

if __name__ == "__main__":
    main()
