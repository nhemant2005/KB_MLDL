# Project Bloat & Efficiency Report

## Detailed File Summaries

| File | Summary | Status / Bloat Identified |
|---|---|---|
| `topics.json` | The core database mapping 134 video topics to metadata, textbook chapters, and relationships. | Clean, but `slug` and `note_type` are missing natively, causing downstream scripts to recalculate them constantly. |
| `playlist_raw.json` | Raw metadata extracted from yt-dlp. | Clean. |
| `mapping.txt` | Hand-authored textbook mapping reference. | Clean. |
| `config.json` (New) | Consolidates paths and page maps. | **New file** created to eliminate hardcoded redundancies across scripts. |
| `populate.py` | A utility script built specifically to regex-replace the `CHAPTER_PAGE_MAP` dictionary into multiple scripts. | **SEVERE BLOAT**. This is an anti-pattern. Eliminated by moving config out to JSON. |
| `scripts/build_topics.py` | Synthesizes `playlist_raw.json` and `mapping.txt` into `topics.json`. | **CRITICAL FLAW**: It did not natively know about `merge_group`, `merge_role`, `note_type`, or `slug`. If run, it would have wiped out our Phase 4 features. **Fix**: Integrated all these computations natively into the build pipeline. |
| `scripts/generate_notes.py` | The main LLM orchestration engine. Iteratively builds prompts and generates markdown. | **BLOAT**: Hardcoded book paths, page maps, classification sets (`TOOLING_TOPICS`, etc.), and ad-hoc slug/path generation. **Fix**: Stripped >100 lines of hardcoded configs. |
| `scripts/wire_vault.py` | Injects YAML frontmatter and backlinks, creates MOCs. | **BLOAT**: Duplicated the exact classification sets from `generate_notes.py` just to add a single YAML tag. Repeated ad-hoc string replacement for slugs. **Fix**: Stripped redundant logic, pulls natively from `topics.json`. |
| `scripts/extract_textbook_sections.py` | Caches PDF text locally. | **BLOAT**: Hardcoded page maps. **Fix**: Now pulls from `config.json`. |
| `scripts/extract_formulas.py` | Regex sweeps markdown for LaTeX. | **BLOAT**: Recomputed ad-hoc topic slugs. **Fix**: Reads `slug` from `topics.json`. |
| `scripts/playlist_extractor.py` & `inspect_pdf_toc.py` | One-off prep scripts. | Clean. No changes needed. |

---

## Action Plan: Eliminating Redundancies & Decreasing Runtime

I have conducted a deep refactoring pass across the entire OS. Here is exactly what was eliminated to increase efficiency:

1. **Eliminated `populate.py` completely.**
   - **Why**: Maintaining Python scripts to regex-replace dictionaries inside other Python scripts is a major anti-pattern and highly fragile. 
   - **How**: Extracted `BOOK_PATHS` and `CHAPTER_PAGE_MAP` into a clean `config.json` at the root.

2. **Centralized Data Computation in `build_topics.py`**
   - **Why**: `generate_notes.py`, `wire_vault.py`, and `extract_formulas.py` were *all* independently recalculating string formatting (e.g., `.replace(" ", "_").replace("-", "_")`) and re-classifying topics (`tooling` vs `concept`). This wasted CPU cycles and created 3 separate points of failure if a category was changed.
   - **How**: `build_topics.py` now calculates `note_type`, `slug`, `merge_group`, and `merge_role` at compile time and saves them to `topics.json`. Downstream scripts now just read the JSON property directly.

3. **Prevented Data Loss (Critical Catch)**
   - **Why**: You originally asked me to manually inject `merge_group` via an update script. If you had run `build_topics.py` again to refresh the playlist, it would have overwritten the JSON and completely wiped out our merged topic architecture!
   - **How**: I hardcoded the Phase 4 merge mappings natively into `build_topics.py` so the OS can be rebuilt from scratch safely.

4. **Shrunk `generate_notes.py` and `wire_vault.py`**
   - Removed ~150 lines of duplicated code (the `TOOLING_TOPICS` arrays, `classify_topic` functions, and `CHAPTER_PAGE_MAP` dictionaries).

This structural refactor dramatically decreases script size, removes all duplicated constants, speeds up execution by skipping redundant string parsing, and makes the architecture strictly one-way (Data flows from `build_topics.py` -> `topics.json` -> Generative Scripts).
