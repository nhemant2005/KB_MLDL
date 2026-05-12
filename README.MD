# ML Curriculum Operating System

A local, fully automated Machine Learning study system that ingests a 134-video YouTube playlist and three major ML textbooks, synthesises structured Obsidian notes using Claude AI, and wires them into a navigable knowledge graph — with zero manual note-taking.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Directory Layout](#architecture--directory-layout)
3. [Full Pipeline Walkthrough](#full-pipeline-walkthrough)
4. [Scripts Reference](#scripts-reference)
5. [Data Files Reference](#data-files-reference)
6. [Libraries & Dependencies](#libraries--dependencies)
7. [External Services & APIs](#external-services--apis)
8. [CLI Reference Cheatsheet](#cli-reference-cheatsheet)
9. [Environment Setup](#environment-setup)

---

## Project Overview

This project treats your ML study plan as software: each topic is a typed object, each note is a compiled artifact, and the knowledge graph is a queryable database. The system is split into three phases:

| Phase | Goal | Status |
|---|---|---|
| **Phase 1 — Ingestion** | Extract playlist metadata and structure topic database | Complete |
| **Phase 2 — Synthesis** | Generate structured Obsidian notes from textbook content using Claude | Complete |
| **Phase 3 — Wiring** | Inject YAML frontmatter, dependency-aware links, MOC files, and study briefs | Complete |

The playlist driving this system is the **CampusX "100 Days of ML"** series. It covers 134 topics across 22 curriculum sections — from Python tooling and EDA all the way through Ensemble Methods, SVMs, and Unsupervised Learning.

---

## Architecture & Directory Layout

```
KB_MLDL/
│
├── .env                         ← API keys (never committed)
├── .gitignore
├── mapping.txt                  ← Authoritative curriculum map: day → textbook chapters
├── topics.json                  ← Full topic database (134 topics)
├── formulas.json                ← Extracted LaTeX formulas (generated after notes exist)
├── notes_progress.json          ← Per-day generation status tracker
├── failed_topics.json           ← Auto-logged API failures
├── playlist_raw.json            ← Raw YouTube playlist data
│
├── scripts/
│   ├── playlist_extractor.py    ← Phase 1: scrapes YouTube playlist metadata
│   ├── build_topics.py          ← Phase 1: builds topics.json from raw playlist + mapping
│   ├── inspect_pdf_toc.py       ← Phase 2 prep: exports PDF table of contents
│   ├── extract_textbook_sections.py ← Phase 2 prep: extracts & caches chapter text from PDFs
│   ├── generate_notes.py        ← Phase 2+3: LLM note generation + --brief study summary
│   ├── extract_formulas.py      ← Phase 3: scans generated notes for LaTeX formulas
│   └── wire_vault.py            ← Phase 3: injects YAML frontmatter, links, and MOC files
│
├── Textbooks/                   ← PDF textbooks (git-ignored)
│   └── extracted/               ← Cached plain-text chapter dumps (git-ignored)
│
└── KB_Obsidian/                 ← Obsidian vault output
    ├── Foundations/
    ├── EDA/
    ├── Feature_Engineering/
    ├── Linear_Regression/
    ├── ...                      ← One folder per curriculum section
    └── [Section]/
        ├── day_NN_topic_name.md ← Generated note
        └── 🗺 [Section] MOC.md  ← Auto-generated Map of Content
```

---

## Full Pipeline Walkthrough

### Step 1 — Scrape the Playlist

```bash
python scripts/playlist_extractor.py "https://www.youtube.com/playlist?list=PLKnIA16_Rmvbr7zKYQuBfsVkjoLcJgxHH"
```

`yt-dlp` fetches video titles, URLs, and durations without downloading any video. Output is saved to `playlist_raw.json`.

---

### Step 2 — Build the Topic Database

```bash
python scripts/build_topics.py
```

Reads `playlist_raw.json` and cross-references `mapping.txt` to produce `topics.json`. Each topic record contains:
- `topic` — clean topic name
- `section` — curriculum section (e.g. "Linear Regression")
- `playlist_day` — day number in the playlist
- `prerequisites` — upstream dependency list
- `textbook_sources` — list of books + chapters with priority levels
- `difficulty`, `interview_importance`, `status`

---

### Step 3 — Inspect PDF Table of Contents

```bash
python scripts/inspect_pdf_toc.py
```

One-time setup step. Opens all three textbook PDFs using PyMuPDF and dumps their embedded table of contents to `toc_output.txt`. Used manually to confirm the correct page ranges for `CHAPTER_PAGE_MAP`.

---

### Step 4 — Extract & Cache Chapter Text

```bash
python scripts/extract_textbook_sections.py
```

Reads every `textbook_sources` entry in `topics.json`, looks up the page range in `CHAPTER_PAGE_MAP`, and extracts raw text from the PDF using PyMuPDF. Each chapter is saved as a plain `.txt` file under `Textbooks/extracted/` so it is only extracted once. On subsequent runs, the cache is used directly — no PDF re-reading.

---

### Step 5 — Generate Notes

```bash
# Single day
python scripts/generate_notes.py --day 51

# Range of days
python scripts/generate_notes.py --days 50-56

# Entire section
python scripts/generate_notes.py --section "Linear Regression"

# Preview what would run (no API call, no file write)
python scripts/generate_notes.py --days 50-56 --dry-run
```

For each topic, the script:
1. Loads the full cached chapter text for every mapped textbook source
2. Classifies the topic into one of four note types: `tooling`, `math_heavy`, `algorithm`, or `concept`
3. Builds a structured prompt embedding the textbook text as the sole source of truth
4. Calls the Claude API (`claude-sonnet-4-6`) with `max_tokens=4000`
5. Saves the generated note to `KB_Obsidian/[Section]/day_NN_topic_name.md`
6. Marks the topic as `done` in `notes_progress.json`
7. Prints a per-topic study summary immediately after generation

Failed generations are automatically logged to `failed_topics.json` for retry.

---

### Step 6 — Extract Formulas

```bash
python scripts/extract_formulas.py
```

Scans every `.md` file in `KB_Obsidian/` for `## Key Formulas` sections, extracts all LaTeX expressions using regex, and cross-references them with `topics.json` metadata. Shows a preview before asking for approval, then writes `formulas.json`. Used by `wire_vault.py` to populate MOC formula sections.

---

### Step 7 — Wire the Vault

```bash
# Wire all generated notes in a specific section + generate its MOC
python scripts/wire_vault.py --section "Linear Regression"

# Wire the entire vault at once (run after generating all 134 notes)
python scripts/wire_vault.py --all

# Preview what would change without writing anything
python scripts/wire_vault.py --section "Linear Regression" --dry-run
```

For each generated note, `wire_vault.py`:
1. Prepends a structured YAML frontmatter block (topic, section, day, difficulty, importance, status, tags, prerequisites)
2. Replaces the raw `Prerequisites:` footer that Claude outputs with a structured `## Links` section containing:
   - **Prerequisites** — upstream topics this note depends on
   - **Unlocks** — downstream topics that list this as a prerequisite
   - **Same Section** — other topics in the same curriculum section
   - **See Also** — cross-section topics that share the same textbooks
3. Generates a `🗺 [Section] MOC.md` file at the root of each section folder containing:
   - Sortable topic table (Day | Topic | Difficulty | Importance | Status)
   - Dependency graph (which topics unlock which)
   - Key formulas from `formulas.json`
   - Ranked revision list sorted by interview importance
   - Deduplicated textbook reading list

---

### Step 8 — Daily Study Brief (no API call)

```bash
# Brief for a single day
python scripts/generate_notes.py --brief --day 26

# Brief for an entire section
python scripts/generate_notes.py --brief --section "Feature Engineering"

# Brief for a range
python scripts/generate_notes.py --brief --days 50-56
```

`--brief` mode never touches the API, never modifies files. It prints:
- Prerequisite dependency status (`[OK]` / `[NO]`)
- Textbook chapters to read today with exact topic coverage pulled from `mapping.txt`
- Key formulas (if `formulas.json` is populated)
- What topics this day unlocks downstream
- Note stats (word count, character count, note type)
- An `obsidian://` deep-link to open the note directly in Obsidian

---

## Scripts Reference

| Script | Phase | One-liner |
|---|---|---|
| `playlist_extractor.py` | 1 | Scrapes YouTube playlist into `playlist_raw.json` using `yt-dlp` |
| `build_topics.py` | 1 | Parses raw playlist + `mapping.txt` into structured `topics.json` |
| `inspect_pdf_toc.py` | 2 prep | Dumps PDF table-of-contents to `toc_output.txt` for page-range mapping |
| `extract_textbook_sections.py` | 2 prep | Extracts full chapter text from PDFs and caches as `.txt` files |
| `generate_notes.py` | 2 + 3 | LLM note orchestration; also handles `--brief` study summaries |
| `extract_formulas.py` | 3 | Parses LaTeX from generated notes into `formulas.json` |
| `wire_vault.py` | 3 | Injects YAML frontmatter, dependency link sections, and section MOC files |
| `populate.py` | utility | Propagates `CHAPTER_PAGE_MAP` into both generate and extract scripts |

---

## Data Files Reference

| File | Generated By | Consumed By | Contents |
|---|---|---|---|
| `playlist_raw.json` | `playlist_extractor.py` | `build_topics.py` | Raw YouTube metadata (title, URL, duration) |
| `topics.json` | `build_topics.py` | Everything | 134-topic database with full curriculum metadata |
| `mapping.txt` | Hand-authored | `build_topics.py`, `generate_notes.py` | Day-by-day textbook chapter mappings |
| `notes_progress.json` | `generate_notes.py` | `generate_notes.py` | Per-day `"done"` flags for skip logic |
| `failed_topics.json` | `generate_notes.py` | Manual review | Topics that errored during generation |
| `formulas.json` | `extract_formulas.py` | `wire_vault.py`, `generate_notes.py` | LaTeX formulas indexed by topic slug |
| `toc_output.txt` | `inspect_pdf_toc.py` | Manual reference | Human-readable PDF table of contents |
| `Textbooks/extracted/*.txt` | `extract_textbook_sections.py` | `generate_notes.py` | Cached plain-text chapter dumps |

---

## Libraries & Dependencies

| Library | Version | Role |
|---|---|---|
| `anthropic` | latest | Official Python SDK for the Claude API |
| `pymupdf` (`fitz`) | latest | PDF parsing — text extraction and TOC reading |
| `yt-dlp` | latest | YouTube playlist metadata scraping (no video download) |
| `python-dotenv` | latest | Loads `.env` file into environment variables at runtime |
| `flake8` | latest | Python linting (development only) |
| `textwrap` | stdlib | Word-wraps textbook coverage text in the study brief output |
| `pathlib` | stdlib | Cross-platform file path handling throughout all scripts |
| `re` | stdlib | LaTeX formula extraction and `mapping.txt` parsing |
| `json` | stdlib | Read/write all `.json` data files |
| `argparse` | stdlib | CLI argument parsing for `generate_notes.py` and `wire_vault.py` |
| `time` | stdlib | API rate-limit safety delay (2 seconds between Claude calls) |

### Install all dependencies

```bash
pip install anthropic pymupdf yt-dlp python-dotenv flake8
```

---

## External Services & APIs

### Anthropic Claude API

- **Model used:** `claude-sonnet-4-6`
- **Purpose:** Generates the actual note content from textbook source material
- **Max output tokens:** 4,000 per note
- **Context window:** Claude Sonnet 4.6's large context window allows sending full textbook chapters (not cropped excerpts) as source material
- **Prompt design:** Four structured templates depending on note type (`tooling`, `math_heavy`, `algorithm`, `concept`). The LLM is explicitly instructed to use only the provided textbook text — never its training data.
- **Auth:** `ANTHROPIC_API_KEY` environment variable loaded from `.env`
- **SDK:** `anthropic` Python package

### YouTube (via yt-dlp)

- **Purpose:** Extracts playlist metadata (titles, URLs, durations) without downloading videos
- **Auth:** None required for public playlists
- **Rate limiting:** `yt-dlp` handles this automatically with the `extract_flat=True` option

---

## CLI Reference Cheatsheet

```bash
# ── PHASE 2: GENERATE NOTES ───────────────────────────────────────────
python scripts/generate_notes.py --day 51
python scripts/generate_notes.py --days 50-56
python scripts/generate_notes.py --section "Linear Regression"
python scripts/generate_notes.py --days 50-56 --dry-run

# ── PHASE 3: STUDY BRIEFS (no API call, no file write) ────────────────
python scripts/generate_notes.py --brief --day 51
python scripts/generate_notes.py --brief --days 50-56
python scripts/generate_notes.py --brief --section "Feature Engineering"

# ── PHASE 3: WIRE VAULT ───────────────────────────────────────────────
python scripts/wire_vault.py --section "Linear Regression"
python scripts/wire_vault.py --section "Linear Regression" --dry-run
python scripts/wire_vault.py --all

# ── PREP SCRIPTS (run once) ───────────────────────────────────────────
python scripts/playlist_extractor.py <playlist_url>
python scripts/build_topics.py
python scripts/inspect_pdf_toc.py
python scripts/extract_textbook_sections.py

# ── FORMULA EXTRACTION ────────────────────────────────────────────────
python scripts/extract_formulas.py
```

---

## Environment Setup

### 1. Clone and install

```bash
git clone <repo-url>
cd KB_MLDL
pip install anthropic pymupdf yt-dlp python-dotenv
```

### 2. Create your `.env` file

```env
ANTHROPIC_API_KEY=sk-ant-...your-key-here...
```

> `.env` is git-ignored. Never commit your API key.

### 3. Add your textbooks

Place your PDF files inside `Textbooks/`. The exact filenames expected by the scripts are defined in `BOOK_PATHS` inside `generate_notes.py`. You can rename the PDFs and update that dictionary if needed.

### 4. Run the pipeline

```bash
# Extract all chapter text (one-time)
python scripts/extract_textbook_sections.py

# Generate notes for a section
python scripts/generate_notes.py --section "Linear Regression"

# Wire the vault for that section
python scripts/wire_vault.py --section "Linear Regression"

# Preview a daily brief at any time
python scripts/generate_notes.py --brief --day 51
```

---

## Textbook Coverage

| Book | Abbreviation | Chapters Used | Coverage |
|---|---|---|---|
| Hands-On Machine Learning (Géron, 2019) | HOML | 1–9, 11, 12 | Primary source for most topics |
| Introduction to Statistical Learning (James et al., 2021) | ISL | 1–9, 12 | Support/reference for statistical foundations |
| Pattern Recognition and Machine Learning (Bishop, 2006) | PRML | 1–7, 12, 14 | Advanced mathematical formulations |

---

## Curriculum Sections

| Section | Days | Topics |
|---|---|---|
| Foundations | 1–18 | What is ML, types, tensors, math prerequisites |
| EDA | 19–24 | Pandas, univariate/bivariate analysis, plotting |
| Feature Engineering | 25–49 | Missing data, encoding, scaling, outliers, pipelines |
| Linear Regression | 50–56 | OLS, normal equation, ridge, assumptions |
| Gradient Descent & Optimisation | 57–64 | Batch/mini-batch/SGD, learning rate |
| Logistic Regression | 65–72 | Binary/multi-class, sigmoid, decision boundary |
| Decision Trees | 73–83 | CART, entropy/gini, pruning, visualisation |
| Ensemble Methods | 84–100 | Bagging, random forests, boosting, XGBoost, stacking |
| Naive Bayes | 101–107 | Gaussian, Bernoulli, multinomial |
| KNN | 108–112 | Distance metrics, curse of dimensionality |
| SVM | 113–120 | Hard/soft margin, kernels |
| PCA | 121–125 | Dimensionality reduction, mathematical formulation |
| Clustering (Unsupervised) | 126–134 | K-means, DBSCAN, hierarchical, XGBoost maths |
