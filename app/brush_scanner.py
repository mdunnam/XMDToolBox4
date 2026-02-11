"""Brush directory scanner.

Scans ZBrush installation directories for ``.ZBP`` files and extracts
their embedded 96×96 thumbnails.  Results are cached in a JSON index
so subsequent launches are fast.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from .config import ASSET_EXTENSIONS, ASSET_SCAN_FOLDERS, DATA_DIR
from .zbp_thumbnail import extract_zbp_thumbnail


# Persistent cache of scanned brushes.
_BRUSH_CACHE_PATH: str = os.path.join(DATA_DIR, "brush_cache.json")
# Directory for cached thumbnails.
_THUMB_CACHE_DIR: str = os.path.join(DATA_DIR, "thumbnails")


@dataclass
class ScannedBrush:
    """A brush discovered on disk."""

    name: str
    path: str
    category: str = ""
    modified: float = 0.0
    thumb_path: str = ""


def scan_brush_directories(
    zbrush_path: str,
    *,
    force: bool = False,
    on_progress: Optional[Callable[[int, int, str], Any]] = None,
) -> list[ScannedBrush]:
    """Scan the ZBrush installation for ``.ZBP`` brush files.

    Args:
        zbrush_path: Root of the ZBrush installation
            (e.g. ``C:/Program Files/Maxon ZBrush 2025``).
        force: If True, ignore the cache and rescan everything.
        on_progress: Optional ``(current, total, name)`` callback.

    Returns:
        A list of :class:`ScannedBrush` instances sorted by name.
    """
    if not zbrush_path or not os.path.isdir(zbrush_path):
        return []

    # Load existing cache.
    cache = _load_cache() if not force else {}

    # Collect candidate .ZBP files from all known brush folders.
    # Use a dict keyed by name to deduplicate across scan directories.
    zbp_by_name: dict[str, tuple[str, str, str]] = {}  # name -> (path, name, category)
    extensions = {ext.lower() for ext in ASSET_EXTENSIONS.get("Brushes", ())}

    for rel_folder in ASSET_SCAN_FOLDERS.get("Brushes", ()):
        scan_root = os.path.join(zbrush_path, rel_folder)
        if not os.path.isdir(scan_root):
            continue
        for dirpath, _dirs, filenames in os.walk(scan_root):
            for fname in filenames:
                if os.path.splitext(fname)[1].lower() not in extensions:
                    continue
                full = os.path.join(dirpath, fname)
                name = os.path.splitext(fname)[0]
                # Category = immediate parent folder name (e.g. "Clay").
                parent = os.path.basename(dirpath)
                if parent.lower() == rel_folder.lower().replace("/", os.sep):
                    parent = ""
                # First occurrence wins (ZBrushes is scanned before ZData).
                if name not in zbp_by_name:
                    zbp_by_name[name] = (full, name, parent)

    zbp_files = list(zbp_by_name.values())
    total = len(zbp_files)
    os.makedirs(_THUMB_CACHE_DIR, exist_ok=True)

    brushes: list[ScannedBrush] = []
    for i, (path, name, category) in enumerate(zbp_files):
        if on_progress:
            on_progress(i + 1, total, name)

        mtime = os.path.getmtime(path)

        # Check cache.
        cached = cache.get(path)
        if cached and cached.get("modified") == mtime:
            brushes.append(ScannedBrush(
                name=cached["name"],
                path=path,
                category=cached.get("category", ""),
                modified=mtime,
                thumb_path=cached.get("thumb_path", ""),
            ))
            continue

        # Extract thumbnail.
        thumb_path = _extract_and_cache_thumb(path, name)

        brush = ScannedBrush(
            name=name,
            path=path,
            category=category,
            modified=mtime,
            thumb_path=thumb_path,
        )
        brushes.append(brush)
        cache[path] = {
            "name": name,
            "category": category,
            "modified": mtime,
            "thumb_path": thumb_path,
        }

    # Save updated cache.
    _save_cache(cache)

    brushes.sort(key=lambda b: b.name.lower())
    return brushes


def _extract_and_cache_thumb(zbp_path: str, name: str) -> str:
    """Extract a ZBP thumbnail and save as a PNG file.

    Args:
        zbp_path: Path to the ``.ZBP`` file.
        name: Brush display name (used for the filename).

    Returns:
        Path to the cached PNG, or empty string on failure.
    """
    rgba = extract_zbp_thumbnail(zbp_path)
    if rgba is None:
        return ""

    # Save as raw RGBA — we'll load via QImage(data, 96, 96, Format_RGBA8888).
    # Using a simple raw file is fastest; no PNG encoding needed.
    safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in name)
    out_path = os.path.join(_THUMB_CACHE_DIR, f"{safe_name}.rgba")
    try:
        with open(out_path, "wb") as f:
            f.write(rgba)
        return out_path
    except OSError:
        return ""


def _load_cache() -> dict:
    """Load the brush scan cache from disk.

    Returns:
        A dict mapping file paths to cached metadata.
    """
    if not os.path.isfile(_BRUSH_CACHE_PATH):
        return {}
    try:
        with open(_BRUSH_CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_cache(cache: dict) -> None:
    """Persist the brush scan cache to disk.

    Args:
        cache: The cache dict to save.
    """
    os.makedirs(os.path.dirname(_BRUSH_CACHE_PATH), exist_ok=True)
    try:
        with open(_BRUSH_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=1)
    except OSError:
        pass
