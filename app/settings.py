"""Persistent application settings backed by a JSON file.

Stores user preferences such as the ZBrush install path, UI options,
and first-run state.  Settings are loaded at startup and saved
automatically whenever a value changes.
"""

from __future__ import annotations

import json
import os
from typing import Any

from .config import DATA_DIR

SETTINGS_PATH: str = os.path.join(DATA_DIR, "settings.json")

# Default values for every known setting.
_DEFAULTS: dict[str, Any] = {
    "first_run_complete": False,
    "zbrush_path": "",
    "single_click_select": False,
    "show_advanced_tooltips": True,
    "show_xmd_category": True,
    "auto_update": True,
}


class AppSettings:
    """Read/write access to the application settings file.

    Settings are kept in memory as a plain dict and flushed to disk
    on every ``set`` call so nothing is lost on a crash.
    """

    def __init__(self, path: str = SETTINGS_PATH) -> None:
        self._path = path
        self._data: dict[str, Any] = dict(_DEFAULTS)
        self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, key: str, default: Any = None) -> Any:
        """Return a setting value, falling back to *default*.

        Args:
            key: The setting name.
            default: Returned when *key* is not present.

        Returns:
            The stored value or *default*.
        """
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Update a setting and persist to disk.

        Args:
            key: The setting name.
            value: The new value.
        """
        self._data[key] = value
        self._save()

    @property
    def zbrush_path(self) -> str:
        """Return the configured ZBrush install directory."""
        return self._data.get("zbrush_path", "")

    @zbrush_path.setter
    def zbrush_path(self, value: str) -> None:
        self.set("zbrush_path", value)

    @property
    def first_run_complete(self) -> bool:
        """Whether the first-run setup has been completed."""
        return bool(self._data.get("first_run_complete", False))

    @first_run_complete.setter
    def first_run_complete(self, value: bool) -> None:
        self.set("first_run_complete", value)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """Load settings from disk, merging with defaults."""
        if not os.path.isfile(self._path):
            return
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                stored = json.load(f)
            if isinstance(stored, dict):
                self._data.update(stored)
        except (json.JSONDecodeError, OSError):
            pass  # Corrupt file — keep defaults.

    def _save(self) -> None:
        """Flush current settings to disk."""
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)
