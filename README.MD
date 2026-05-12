# Universal Curriculum Operating System (UCOS)

A universal, fully automated study system that ingests YouTube playlists and relevant textbooks, synthesizes structured knowledge bases using any LLM (Claude, GPT, etc.), and wires them into a navigable Obsidian vault — with zero manual note-taking.

While the architecture is universal, this instance is currently configured for the **CampusX "100 Days of ML"** playlist.

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

This project treats your learning plan as software: each topic is a typed object, each note is a compiled artifact, and the knowledge graph is a queryable database. The system is designed to be **curriculum-agnostic**: you provide the playlist URL, the textbook PDFs, and the prompt templates, and the OS handles the rest.

### Key Universal Features
- **Model Independence**: Swap between Claude, GPT-4, or local models via `user_config.json`.
- **Iterative Synthesis**: Automatically breaks down complex, multi-video topics into deep, section-by-section notes to bypass LLM output limits.
- **Context Injection**: Directly maps specific textbook chapters to videos, ensuring the LLM writes from primary sources, not hallucinations.
- **Obsidian Wiring**: Auto-generates Maps of Content (MOCs), dependency-aware backlinks, and LaTeX formula indexes.

> **Current Implementation**: This repository is currently populated with the **CampusX "100 Days of ML"** curriculum map (134 topics, 22 sections, and 3 reference textbooks).

---

## Architecture & Directory Layout

```
KB_MLDL/
│
├── user_config.json             ← THE CONTROL PANEL: Change model, playlist, paths, and prompts here.
├── config.json                  ← Architecture defaults (page maps, etc.)
├── .env                         ← API keys (never committed)
├── mapping.txt                  ← Curriculum map: day → textbook chapters
├── topics.json                  ← Full topic database (compiled by build_topics.py)
├── notes_progress.json          ← Generation status tracker
├── playlist_raw.json            ← Raw YouTube playlist data
│
├── scripts/
│   ├── cfg.py                   ← Configuration loader (Single Source of Truth)
│   ├── playlist_extractor.py    ← Phase 1: scrapes YouTube playlist metadata
│   ├── build_topics.py          ← Phase 1: builds topics.json
│   ├── extract_textbook_sections.py ← Phase 2 prep: extracts & caches chapter text
│   ├── generate_notes.py        ← Phase 2: LLM note generation + --brief summary
│   ├── wire_vault.py            ← Phase 3: injects YAML, links, and MOC files
│   └── extract_formulas.py      ← Phase 3: scans notes for LaTeX formulas
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
- `merge_group` / `merge_role` — groups multi-day topics into single notes
- `difficulty`, `interview_importance`, `status`

---

---

### Step 3 — Extract & Cache Chapter Text

```bash
python scripts/extract_textbook_sections.py
```

Reads every `textbook_sources` entry in `topics.json`, looks up the page range in `CHAPTER_PAGE_MAP`, and extracts raw text from the PDF using PyMuPDF. Each chapter is saved as a plain `.txt` file under `Textbooks/extracted/` so it is only extracted once. On subsequent runs, the cache is used directly — no PDF re-reading.

---

### Step 4 — Generate Notes

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

For each topic, the script handles either **Standalone** or **Merged** logic:
1. **Standalone Days**: Classifies the topic (`tooling`, `algorithm`, etc.) and generates a structured note in a single API call using the textbook text.
2. **Merged Groups (e.g., Days 50-56 for Linear Regression)**: Aggregates chapters and iteratively generates the note **section-by-section** (Math, Intuition, Code) with independent API calls. This preserves maximum depth and bypasses LLM output token limits.
  
Finally, the script saves the note to `KB_Obsidian/[Section]/`, marks the day(s) as `done` in `notes_progress.json`, and prints a detailed study summary.

Failed generations are automatically logged to `failed_topics.json` for retry.

---

### Step 5 — Extract Formulas

```bash
python scripts/extract_formulas.py
```

Scans every `.md` file in `KB_Obsidian/` for `## Key Formulas` sections, extracts all LaTeX expressions using regex, and cross-references them with `topics.json` metadata. Shows a preview before asking for approval, then writes `formulas.json`. Used by `wire_vault.py` to populate MOC formula sections.

---

### Step 6 — Wire the Vault

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

### Step 7 — Daily Study Brief (no API call)

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

*Note: For merged topics, `--brief` automatically prints a unified summary aggregating prerequisites and textbook chapters across all days in the group.*

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

---

## Data Files Reference

| File | Generated By | Consumed By | Contents |
|---|---|---|---|
| `playlist_raw.json` | `playlist_extractor.py` | `build_topics.py` | Raw YouTube metadata (title, URL, duration) |
| `topics.json` | `build_topics.py` | Everything | 134-topic database with metadata and `merge_group` flags |
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

### LLM Orchestration
- **Model Agnostic:** Change `model` in `user_config.json` to any supported model (e.g., `claude-3-5-sonnet`, `gpt-4o`, etc.).
- **Iterative Merged Logic:** For multi-video topics, the system generates notes section-by-section to bypass output token limits.
- **Context Integrity:** Full textbook chapters are sent as source material, with strict instructions to use ONLY provided text.
- **Prompt Templates:** All system and user prompt templates are editable in `user_config.json`.

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

### 3. Configure the System
Edit `user_config.json` to set your:
- LLM model
- Playlist URL
- Textbook PDF paths and page mappings
- Custom prompt templates

### 4. Add your textbooks
Place your PDF files inside `Textbooks/` and ensure the paths in `user_config.json` match the filenames.

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
