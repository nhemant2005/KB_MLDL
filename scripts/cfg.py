"""
cfg.py — Single source of truth for all user and architecture config.

Every script imports from here. Never hardcode paths, models, or prompts
directly in the generator or wiring scripts.

Load order:
  1. config.json       — architecture defaults (page maps, etc.)
  2. user_config.json  — user overrides (wins over config.json)
"""

import json
from pathlib import Path

_ROOT = Path(__file__).parent.parent  # KB_MLDL/


def _load(path: Path) -> dict:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


_arch = _load(_ROOT / "config.json")
_user = _load(_ROOT / "user_config.json")

# ── API / Provider ─────────────────────────────────────────────────────────────
_api            = _user.get("api", {})
API_PROVIDER:  str  = _api.get("provider",    "deepseek")
API_BASE_URL:  str  = _api.get("base_url",    "https://api.deepseek.com/v1")
MODEL:         str  = _api.get("model",       "deepseek-v4-pro")
API_KEY_ENV:   str  = _api.get("api_key_env", "DEEPSEEK_API_KEY")

PLAYLIST_URL: str = _user.get("playlist_url", "")

# ── Vault ──────────────────────────────────────────────────────────────────────
VAULT_OUTPUT_DIR: str = _user.get("vault_output_dir", "KB_Obsidian")

# ── Books & Page Maps ──────────────────────────────────────────────────────────
# user_config books block → extract paths
_user_books = _user.get("books", {})
BOOK_PATHS: dict = (
    {k: v["path"] for k, v in _user_books.items()}
    if _user_books
    else _arch.get("BOOK_PATHS", {})
)

# Chapter page map: user overrides arch
CHAPTER_PAGE_MAP: dict = _user.get(
    "chapter_page_map", _arch.get("CHAPTER_PAGE_MAP", {})
)

# ── Generation Params ──────────────────────────────────────────────────────────
_gen = _user.get("generation", {})
RATE_LIMIT_SLEEP:           int  = _gen.get("api_rate_limit_sleep_seconds", 2)
MERGED_NOTE_MAX_TOKENS:     int  = _gen.get("merged_note_max_tokens", 2000)
STANDALONE_NOTE_MAX_TOKENS: int  = _gen.get("standalone_note_max_tokens", 4000)


# ── Prompts ────────────────────────────────────────────────────────────────────
_prompts = _user.get("prompts", {})

SHARED_RULES: str = _prompts.get(
    "shared_rules",
    "- Use ONLY the textbook content provided.\n"
    "- Source every claim: (HOML ch.4)\n"
    "- LaTeX for all math.\n"
    "- Output ONLY the markdown note.",
)

_type_headers = _prompts.get("note_type_headers", {})
_type_templates = _prompts.get("note_type_templates", {})


def get_note_header(note_type: str, playlist_day: int) -> str:
    """Returns the system-level header for a given note type, with day injected."""
    raw = _type_headers.get(note_type, _type_headers.get("concept", ""))
    return raw.replace("{playlist_day}", str(playlist_day))


def get_note_template(note_type: str, importance: int = 5, **kwargs) -> str:
    """
    Returns the body template for the note type.
    For 'algorithm', selects the right tier based on importance:
      >= 9 → algorithm_high
      >= 7 → algorithm_medium
      else → algorithm_low
    """
    if note_type == "algorithm":
        if importance >= 9:
            key = "algorithm_high"
        elif importance >= 7:
            key = "algorithm_medium"
        else:
            key = "algorithm_low"
    else:
        key = note_type

    raw = _type_templates.get(key, _type_templates.get("concept", ""))
    for k, v in kwargs.items():
        raw = raw.replace("{" + k + "}", str(v))
    return raw
