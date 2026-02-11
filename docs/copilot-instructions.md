# Copilot Instructions for XMD ToolBox

These instructions apply to all code created for this project.
**Read `docs/plugin-plan.md` first** — it is the single source of truth for architecture,
current status, and what to work on next.

## Project Overview

XMD ToolBox 4.0 is an external PySide6 desktop app for organizing ZBrush assets.
It has a lightweight ZBrush-side bridge plugin for command execution via file-based IPC.

- **Active code lives in `app/`** — this is the PySide6 desktop application.
- **`zbrush_plugin/xmd_bridge.py`** — the ZBrush-side bridge (runs inside ZBrush's Python VM).
- **`xmd_toolbox/`** — legacy code from an earlier approach. May be removed. Do not extend it.
- **`docs/plugin-plan.md`** — architecture, status tables, resolved decisions, next steps.

## How to Run

```
cd D:\Perforce\_APPS_Python\XMDToolBox
.venv\Scripts\python.exe app/main.py
```

Dependencies: `PySide6>=6.10`, `PySide6-QtAds>=4.5`. Install via `.venv` and `requirements.txt`.

## General

- Follow clean code principles.
- Prefer clarity over cleverness.
- Minimize side effects and shared global state.
- Keep functions focused and small.
- Add JSDoc/docstring comments to all public functions.

## Python Style

- Use type hints for all public functions and method signatures.
- Use docstrings (Google style) for all functions and classes.
- Use `from __future__ import annotations` at the top of every module.
- Keep line length at or under 120 characters when practical.
- Avoid modifying shared module state (`sys`, `math`, `random`).
- Prefer `dataclass` for data models.
- Prefer `Optional[X]` over `X | None` for compatibility.

## PySide6 / Qt Conventions

- Use `PySide6`, not `PyQt6`. Import paths are `PySide6.QtCore`, `PySide6.QtGui`, `PySide6.QtWidgets`.
- Docking uses `PySide6QtAds` (Qt Advanced Docking System), imported as `import PySide6QtAds as ads`.
- Signals use `Signal()` (not `pyqtSignal`). Slots use `@Slot()` decorator.
- Theme is in `app/theme.py` — all styling is QSS-based, applied globally.
- Surface color hierarchy: `#121214` → `#1C1C1E` → `#252528` → `#2E2E32` → `#38383D`.
- Accent color: `#E8652B` (warm orange).
- All icons are SVG, stored in `app/icons/`, 20×20 viewBox, 32×32 display size.

## ZBP Thumbnail Extraction — CRITICAL

**Do not casually rewrite `app/zbp_thumbnail.py`.**

This is a careful port of Pixologic's C++ `ReadZBrushFileThumbnail` function (by Ofer Alon).
The original C++ source is in `mdunnam/XMDToolBox4.0` repo, file `Util/brushiconimageprovider.cpp`.

Key facts:
- Magic pattern scan: `00 90 00 00 04 00 80 01` starting at byte offset 200.
- Compression version is 6 bytes before the magic.
- v4: four 2-byte block sizes. v5+: 12-byte skip then two 4-byte block sizes.
- RLE: positive byte = repeat count, negative (>127) = literal run of `256 - n` bytes, 0 = end.
- v6+: extra 4-byte skip per block before RLE data.
- Data is planar within each block — decompressed bytes are interleaved into 4 sub-channels.
- R↔B swap happens inline during the alpha channel (sub_ch 3) write loop.
- Alpha is optionally boosted: `min(prev² * 0.5, 255)`.
- Output: 96×96 RGBA, 36864 bytes. Cached as raw `.rgba` files (not PNG).

If thumbnails look wrong:
- All blue → R↔B swap is being applied twice or not at all.
- Tiled 3×3 → treating data as interleaved RGBA instead of planar blocks.
- Garbled → wrong compression version handling or block offset math.

## Brush Scanner

`app/brush_scanner.py` scans three directories under the ZBrush install path:
1. `ZBrushes` — shipped brushes (always present)
2. `ZData/BrushPresets` — user presets, ZBrush 2026.1+
3. `ZStartup/BrushPresets` — user presets, pre-2026.1

Deduplication: by brush name. First directory scanned wins (ZBrushes first).
Cache: `app/data/brush_cache.json` (keyed by file path + mtime).
Thumbnails: `app/data/thumbnails/{safe_name}.rgba`.

## Settings System

- `app/settings.py` — `AppSettings` class, JSON-backed, auto-saves on property change.
- `app/settings_dialog.py` — full settings dialog with category sidebar.
- `app/setup_dialog.py` — first-run wizard (ZBrush path selection).
- `app/zbrush_detect.py` — auto-detect ZBrush installs from registry + Program Files.
- Settings stored at `app/data/settings.json`.
- Key setting: `zbrush_path` — root of ZBrush installation (e.g. `C:/Program Files/Maxon ZBrush 2025`).

## ZBrush Bridge Constraints

These apply ONLY to code in `zbrush_plugin/` that runs inside ZBrush's Python VM:

- The Python VM is shared and persistent inside ZBrush.
- No `multiprocessing`. No `subprocess` with `sys.executable`.
- Do not override `sys.stdin`/`stdout`/`stderr`.
- Do not change the working directory (it's the ZBrush app dir).
- Clean up any `sys.path` modifications after importing.
- Prefer absolute paths for all file operations.

## Reference Code

The old C++/Qt ToolBox 4.0 has working implementations for all resource types:
- **Repo:** `mdunnam/XMDToolBox4.0`, branch `trunk`
- **Brush icons:** `Util/brushiconimageprovider.cpp` (C++ ReadZBrushFileThumbnail)
- **Alpha icons:** `Util/alphaiconimageprovider.cpp` (uses Qt ImageReader + DevIL fallback)
- **Brush scanning:** `Model/brushdataservice.cpp` (recursive .ZBP scan)
- **ZBrush commands:** `Model/zbrushcommander.cpp` (activate brush, reset, etc.)
- **Architecture overview:** `ARCHITECTURE.md` (1200+ lines of detailed docs)

Use the `github_repo` tool to search this repo when implementing new resource types.
