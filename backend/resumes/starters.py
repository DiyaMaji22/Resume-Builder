"""Starter resume templates and benchmark job descriptions, loaded once from JSON."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_DATA_FILE = Path(__file__).resolve().parent / "data" / "starters.json"


@lru_cache(maxsize=1)
def load_catalog() -> dict[str, Any]:
    """Returns ``{"starters": [...], "benchmarkJobs": [...]}`` in API shape."""
    with _DATA_FILE.open(encoding="utf-8") as handle:
        catalog: dict[str, Any] = json.load(handle)
    return catalog
