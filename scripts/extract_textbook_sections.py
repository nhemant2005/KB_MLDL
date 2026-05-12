import fitz
import json
from pathlib import Path



with open("config.json") as f:
    config = json.load(f)
BOOK_PATHS = config["BOOK_PATHS"]
CHAPTER_PAGE_MAP = config["CHAPTER_PAGE_MAP"]

def extract_chapter(book: str, chapter: str) -> str:
    cache_path = Path(
        f"textbooks/extracted/{book.lower()}_ch{chapter}.txt"
    )
    if cache_path.exists():
        print(f"  [cache hit] {book} ch.{chapter}")
        return cache_path.read_text(encoding="utf-8")

    if str(chapter) not in [str(k) for k in CHAPTER_PAGE_MAP[book]]:
        print(
            f"  [MISSING] {book} ch.{chapter} "
            f"not in CHAPTER_PAGE_MAP — skipping"
        )
        return ""

    doc = fitz.open(BOOK_PATHS[book])
    # Ensure chapter is treated as string for dict lookup since JSON loads it as string/int depending on source
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
    print(f"  [extracted] {book} ch.{chapter} -> {cache_path}")
    return text

# Extract all chapters referenced in topics.json
with open("topics.json") as f:
    topics = json.load(f)

needed = set()
for topic in topics:
    for source in topic.get("textbook_sources", []):
        for ch in source.get("chapters", []):
            needed.add((source["book"], str(ch)))

missing_from_map = []
print(f"\nExtracting {len(needed)} unique chapter/book combinations...\n")
for book, chapter in sorted(needed):
    result = extract_chapter(book, chapter)
    if not result:
        missing_from_map.append(f"{book} ch.{chapter}")

print("\n[OK] Extraction complete.")
print("  Files saved to: textbooks/extracted/")
if missing_from_map:
    print(f"\n  [WARNING] MISSING FROM PAGE MAP ({len(missing_from_map)}):")
    for m in missing_from_map:
        print(f"    - {m}")
    print("  Fix CHAPTER_PAGE_MAP before generating notes.")
