# Changelog

All notable changes to the ML Curriculum OS project will be documented in this file.

## [Unreleased]
### Added
- **Iterative Generation for Merged Notes**: Upgraded `generate_notes.py` to compile merged notes section-by-section. This bypasses LLM output token limits, ensuring that mathematical formulations, code implementations, and intuition sections retain full textbook depth without being truncated.
- **Merge Group Tracking**: Added `merge_group` and `merge_role` to `topics.json`. Topics spanning multiple days (e.g., Linear Regression across Days 50-56) are now aggregated into single comprehensive Obsidian notes.
- **Group Briefs**: Enhanced the `--brief` CLI flag in `generate_notes.py` to print unified group summaries, aggregating prerequisites and textbook chapters for merged days.
- **User Config Layer (`user_config.json` + `cfg.py`)**: Separated all user-facing settings from core architecture into a single `user_config.json`. Users can now change the LLM model, playlist URL, textbook file paths, chapter page maps, API token limits, rate-limiting delay, and all per-note-type prompt templates without touching any Python code. A new `scripts/cfg.py` module acts as the single import point for all downstream scripts.

### Pending / Incomplete
- **Anthropic Prompt Caching**: Plan to implement server-side caching for textbook context blocks to reduce input token costs by ~90% for iterative merged note generation.
  - **Infrastructure Ready**: `user_config.json` and `cfg.py` already include the `prompt_caching` flag.
  - **Remaining Work**: Need to refactor `generate_notes.py` to use structured message blocks with `cache_control: {"type": "ephemeral"}` specifically for the `TEXTBOOK CONTENT` sections.


### Changed
- **System-Wide Refactoring & Bloat Removal**: Executed a massive architectural cleanup:
  - Eliminated `populate.py` by centralizing `BOOK_PATHS` and `CHAPTER_PAGE_MAP` into a clean `config.json` file.
  - Centralized data computation: `build_topics.py` now calculates `note_type`, `slug`, `merge_group`, and `merge_role` at compile time and stores them in `topics.json`. Downstream scripts (`generate_notes.py`, `wire_vault.py`) now just read these fields instead of wastefully re-calculating string manipulations and classifications.
  - Hardcoded Phase 4 merge mappings natively into `build_topics.py` to prevent data loss upon future playlist rebuilds.
  - Shrunk `generate_notes.py` and `wire_vault.py` by over 150 lines by removing redundant categorization logic and constants.

## [Phase 2] - Vault Wiring & Study Briefs
### Added
- **Vault Wiring Engine**: Created `wire_vault.py` to inject structured YAML frontmatter, dependency-aware backlinks, and section-specific Maps of Content (MOCs) into generated Obsidian notes.
- **Study Briefs**: Implemented the `--brief` CLI flag in `generate_notes.py` for generating actionable daily study summaries without triggering API calls or file modifications.
- **Status Tracking**: Integrated automatic prerequisite verification and status tracking into the study summaries to enforce the curriculum workflow.
- **Naming Conventions**: Enforced `day_{day}_{slug}.md` naming convention across all generation scripts to maintain Vault consistency.

## [Phase 1] - Local Curriculum OS Foundation
### Added
- **Curriculum Database Engine**: Established a pure Python, JSON, and Markdown pipeline to ingest a 100-Day Machine Learning YouTube playlist.
- **Data Cleaning & Categorization**: Automated extraction of metadata and textbook mappings into a clean, structured `topics.json` database.
- **Note Generation Foundation**: Created `generate_notes.py` to interface with the Claude API, mapping textbook content to specific playlist days and generating formatted Obsidian markdown notes.
