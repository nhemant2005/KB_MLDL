import fitz  # pip install pymupdf

BOOKS = {
    "HOML": "Textbooks/[2] Aurélien Géron - Hands-On Machine Learning with Scikit-Learn, Keras, and Tensorflow_ Concepts, Tools, and Techniques to Build Intelligent System (2019, O’Reilly Media) - libgen.li.pdf",
    "ISL":  "Textbooks/[Springer Texts in Statistics] Gareth James, Daniela Witten, Trevor Hastie, Robert Tibshirani - An Introduction to Statistical Learning - with Applications in R (2021, Springer Science+Business Media) - libgen.li.pdf",
    "PRML": "Textbooks/[Information Science and Statistics ] Christopher M. Bishop - Pattern Recognition and Machine Learning (2006, Springer) - libgen.li.pdf"
}

with open("toc_output.txt", "w", encoding="utf-8") as f:
    for name, path in BOOKS.items():
        f.write(f"\n{'='*60}\n")
        f.write(f"  {name} — Table of Contents\n")
        f.write(f"{'='*60}\n")
        doc = fitz.open(path)
        toc = doc.get_toc()
        if not toc:
            f.write("  [No embedded TOC — printing page count only]\n")
            f.write(f"  Total pages: {doc.page_count}\n")
        else:
            for level, title, page in toc:
                f.write(f"  p.{page:<5} {'  ' * (level-1)}{title}\n")
