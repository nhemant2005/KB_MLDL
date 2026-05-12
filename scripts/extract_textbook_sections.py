import fitz
import json
from pathlib import Path

BOOK_PATHS = {
    "HOML": "Textbooks/[2] Aurélien Géron - Hands-On Machine Learning with Scikit-Learn, Keras, and Tensorflow_ Concepts, Tools, and Techniques to Build Intelligent System (2019, O’Reilly Media) - libgen.li.pdf",
    "ISL":  "Textbooks/[Springer Texts in Statistics] Gareth James, Daniela Witten, Trevor Hastie, Robert Tibshirani - An Introduction to Statistical Learning - with Applications in R (2021, Springer Science+Business Media) - libgen.li.pdf",
    "PRML": "Textbooks/[Information Science and Statistics ] Christopher M. Bishop - Pattern Recognition and Machine Learning (2006, Springer) - libgen.li.pdf"
}

# ← Filled by me after TOC output is pasted
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
