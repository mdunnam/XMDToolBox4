"""Plugin entry point for XMD ToolBox.

This module is executed on startup when installed via PYTHONPATH or ZBRUSH_PLUGIN_PATH.
"""

from __future__ import annotations

from zbrush import commands as zbc

from . import ui
from .config import PALETTE_NAME


def initialize() -> None:
    """Initialize the plugin and build the UI."""
    ui.build_palette(PALETTE_NAME)


if __name__ == "__main__":
    initialize()
