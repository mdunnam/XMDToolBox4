"""Utility helpers for XMD ToolBox."""

from __future__ import annotations

import os


def get_script_dir() -> str:
    """Return the directory of this package on disk."""
    return os.path.dirname(os.path.abspath(__file__))
