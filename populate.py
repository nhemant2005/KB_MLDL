import re

map_str = '''CHAPTER_PAGE_MAP = {
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
}'''

for fname in ['scripts/extract_textbook_sections.py', 'scripts/generate_notes.py']:
    with open(fname, 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(r'CHAPTER_PAGE_MAP = \{\n\s+\"HOML\":\s+\{\},\n\s+\"ISL\":\s+\{\},\n\s+\"PRML\":\s+\{\}\n\}', map_str, content)
    with open(fname, 'w', encoding='utf-8') as f:
        f.write(content)
