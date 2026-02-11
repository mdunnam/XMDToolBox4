"""Configuration constants for the XMD ToolBox external application."""

from __future__ import annotations

import os

APP_NAME: str = "XMD ToolBox"
APP_VERSION: str = "4.0.0-dev"

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
# File extensions per asset type (used for directory scanning).
# Derived from ZBrush known file types.
# ---------------------------------------------------------------------------
ASSET_EXTENSIONS: dict[str, tuple[str, ...]] = {
    "Brushes": (".ZBP",),
    "Alphas": (".psd", ".bmp", ".jpg", ".jpeg", ".png", ".tif", ".tiff"),
    "Textures": (".psd", ".bmp", ".jpg", ".jpeg", ".png", ".tif", ".tiff"),
    "Materials": (".zmt",),
    "Fibers": (".zfp",),
    "Tools": (".ztl",),
    "Lights": (".ZBP",),  # Light presets share brush extension in some configs.
    "Projects": (".zpr",),
    "Grids": (".zgr",),
    "Array Mesh": (".zam",),
    "Spotlights": (".zsl",),
    "Render Presets": (".zrp",),
    "Documents": (".zbr",),
}

# ---------------------------------------------------------------------------
# Known ZBrush sub-folders per asset type (relative to ZBrush install root).
# ---------------------------------------------------------------------------
ASSET_SCAN_FOLDERS: dict[str, tuple[str, ...]] = {
    "Brushes": ("ZBrushes", "ZData/BrushPresets", "ZStartup/BrushPresets"),
    "Materials": ("ZMaterials", "ZData/Materials", "ZStartup/Materials"),
    "Tools": ("ZTools",),
    "Fibers": ("ZFibersPresets",),
    "Projects": ("ZProjects",),
    "Grids": ("ZGrids",),
    "Array Mesh": ("ZArraysPresets",),
    "Spotlights": ("ZSpotlights",),
    "Render Presets": ("ZRenderPresets",),
    "Documents": ("ZDocs",),
}

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

_APP_DIR: str = os.path.dirname(os.path.abspath(__file__))
DATA_DIR: str = os.path.join(_APP_DIR, "data")
LOCAL_METADATA_PATH: str = os.path.join(DATA_DIR, "brush_metadata.json")
LAYOUT_STATE_PATH: str = os.path.join(DATA_DIR, "dock_layout.xml")

# Default IPC directory — command files are written here for ZBrush to read.
IPC_DIR: str = os.path.join(DATA_DIR, "ipc")

# ---------------------------------------------------------------------------
# Icons.
# ---------------------------------------------------------------------------

ICONS_DIR: str = os.path.join(_APP_DIR, "icons")

# Maps panel / tab display names to SVG icon filenames.
TAB_ICONS: dict[str, str] = {
    "Brushes": "brushes.svg",
    "Alphas": "alphas.svg",
    "Textures": "textures.svg",
    "Materials": "materials.svg",
    "Fibers": "fibers.svg",
    "Tools": "tools.svg",
    "Lights": "lights.svg",
    "Projects": "projects.svg",
    "Grids": "grids.svg",
    "Array Mesh": "array_mesh.svg",
    "Spotlights": "spotlights.svg",
    "Render Presets": "render_presets.svg",
    "Documents": "documents.svg",
    "Favorites": "favorites.svg",
    "Metadata": "metadata.svg",
}
