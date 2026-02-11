"""Local JSON-file metadata store for XMD ToolBox.

This module provides a file-backed metadata store used during development.
It will be replaced or supplemented by the S3 backend when that is implemented.
"""

from __future__ import annotations

import json
import os
from typing import Any

from .models import BrushMetadata


class LocalStore:
    """Read and write brush metadata to a local JSON file.

    The file is a JSON object keyed by brush name.
    """

    def __init__(self, path: str) -> None:
        """Initialize the store.

        Args:
            path: Absolute path to the JSON metadata file.
        """
        self._path: str = path
        self._cache: dict[str, dict[str, Any]] = {}
        self._load()

    # --- public API ---

    def list_brushes(self) -> list[str]:
        """Return all known brush names.

        Returns:
            A sorted list of brush name strings.
        """
        return sorted(self._cache.keys())

    def get_brush(self, name: str) -> BrushMetadata:
        """Return metadata for a brush, creating a default entry if missing.

        Args:
            name: The brush name.

        Returns:
            The BrushMetadata for the brush.
        """
        if name not in self._cache:
            self._cache[name] = BrushMetadata(name=name).to_dict()
            self._save()
        return BrushMetadata.from_dict(self._cache[name])

    def put_brush(self, meta: BrushMetadata) -> None:
        """Persist metadata for a brush.

        Args:
            meta: The BrushMetadata to store.
        """
        self._cache[meta.name] = meta.to_dict()
        self._save()

    def get_favorites(self) -> list[str]:
        """Return brush names marked as favorites.

        Returns:
            A sorted list of favorite brush name strings.
        """
        return sorted(
            name for name, data in self._cache.items() if data.get("favorite", False)
        )

    def search(self, query: str) -> list[str]:
        """Return brush names matching a simple case-insensitive substring search.

        Searches across name, description, brush_type, category, tags, and author.

        Args:
            query: The search string.

        Returns:
            A sorted list of matching brush name strings.
        """
        q = query.lower()
        results: list[str] = []
        for name, data in self._cache.items():
            searchable = " ".join([
                data.get("name", ""),
                data.get("description", ""),
                data.get("brush_type", ""),
                data.get("category", ""),
                " ".join(data.get("tags", [])),
                data.get("author", ""),
            ]).lower()
            if q in searchable:
                results.append(name)
        return sorted(results)

    # --- file IO ---

    def _load(self) -> None:
        """Load the JSON file into the in-memory cache."""
        if os.path.isfile(self._path):
            try:
                with open(self._path, "r", encoding="utf-8") as fh:
                    self._cache = json.load(fh)
            except (json.JSONDecodeError, OSError):
                self._cache = {}
        else:
            self._cache = {}

    def _save(self) -> None:
        """Write the in-memory cache to the JSON file."""
        directory = os.path.dirname(self._path)
        if directory and not os.path.isdir(directory):
            os.makedirs(directory, exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as fh:
            json.dump(self._cache, fh, indent=2, ensure_ascii=False)
