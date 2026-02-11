"""Configuration constants for the plugin."""

from __future__ import annotations

import os

PALETTE_NAME: str = "XMD ToolBox"
SUBPALETTE_MAIN: str = "Main"

# ---------------------------------------------------------------------------
# Asset tabs. Expand as new asset types are confirmed.
# ---------------------------------------------------------------------------
ASSET_TABS: tuple[str, ...] = (
    "Brushes",
    "Alphas",
    "Textures",
    "Materials",
    "Fibers",
    "Tools",
    "Lights",
    "Projects",
    "Grids",
    "Array Mesh",
    "Spotlights",
    "Render Presets",
    "Documents",
)

DEFAULT_ASSET_TAB: str = "Brushes"

# ---------------------------------------------------------------------------
# Brush type labels.
# Derived from the ZBrush brush type taxonomy.
# ---------------------------------------------------------------------------
BRUSH_TYPES: tuple[str, ...] = (
    # Sculpting
    "Standard",
    "Stroke",
    "Stroke Curve",
    "Deco Curve",
    "Alpha Curve",
    "Drop",
    "Curve",
    # Modifying
    "Planar, Trim & Polish",
    "Smooth",
    "Move",
    "Mallet",
    "Buildup",
    "Layer",
    "Nudge",
    "Clay",
    "Snakehook",
    "Spray",
    "Elastic",
    "Colored Spray",
    "Magnify",
    "Drop Dot",
    "Pinch",
    "Line",
    "Morph",
    "Bevel",
    "Project",
    "Extrude",
    "Blur",
    "Scribe",
    "Displace",
    "Pattern",
    "Inflate",
    "Pump",
    # Editing
    "Clip",
    "Noise",
    "Masking",
    "Snake Curve",
    "Select",
    "Pen",
    "Cloth",
    "Contrast",
    "Groom",
    "Knife",
    # Dynamic
    "Dynamic",
    # Geometry
    "Mesh",
    "ZModeler",
    # Utility
    "Vector",
    "Topo",
    # Insert
    "Insert",
    "Insert MultiMesh",
    "Insert MultiMesh Curve",
    # Chisel
    "Chisel",
)

# ---------------------------------------------------------------------------
# Paths and storage.
# ---------------------------------------------------------------------------

# Default directory to scan for brush files. Users can change this at runtime.
DEFAULT_BRUSH_PATH: str = ""

# Local metadata file path (relative to the package directory).
_PACKAGE_DIR: str = os.path.dirname(os.path.abspath(__file__))
LOCAL_METADATA_PATH: str = os.path.join(_PACKAGE_DIR, "data", "brush_metadata.json")
