# XMD ToolBox Plan (ZBrush 2026.1)

> **Last updated:** 2026-02-11 — End of brush grid + thumbnail extraction session.
> **Current state:** Brush panel fully functional with thumbnail grid. Settings system,
> first-run setup, and ZBrush auto-detect complete. Ready for polish and next asset types.

This plan defines the architecture and workflow for the XMD ToolBox 4.0 — an external
PySide6 desktop application that organizes ZBrush assets, with a lightweight ZBrush-side
bridge plugin for command execution.

**This document is the single source of truth for the project.**

## Goals

- Build an external PySide6 (Python 3.11.9) desktop application for asset organization.
- Provide a lightweight ZBrush-side bridge plugin compatible with ZBrush 2026.1 (CPython 3.11.9).
- Follow the ZBrush SDK style guide and shared-VM constraints for the bridge plugin only.
- Focus on ZBrush first; architecture should allow later multi-DCC use (Painter, Blender).
- Provide asset organization, metadata, search, and favorites.

## Architecture

- **External app** (`app/`): PySide6 desktop GUI. Runs in its own Python 3.11.9 venv.
  Full-featured UI with tabs, metadata editing, search, favorites, and settings.
- **ZBrush bridge** (`zbrush_plugin/`): Minimal Python script loaded inside ZBrush.
  Reads IPC command files and executes ZBrush SDK calls. Adds one palette button.
- **Communication**: File-based IPC. The app writes JSON command files; the bridge reads and
  deletes them on poll. No sockets or threading in ZBrush.

## ZBrush Bridge Constraints

- The Python VM is shared and persistent inside ZBrush.
- No multiprocessing. No subprocess with sys.executable.
- Avoid modifying shared module state.
- Do not override sys.stdin/stdout/stderr.
- Working directory is the ZBrush app directory — use absolute paths.

## Folder Structure

```
XMDToolBox/
├── app/                      # External PySide6 application
│   ├── __init__.py
│   ├── main.py               # Entry point (first-run gate → main window)
│   ├── main_window.py        # Main window with dockable panels + toolbar
│   ├── models.py             # Data models (BrushMetadata)
│   ├── local_store.py        # Local JSON metadata store (dev)
│   ├── config.py             # Constants, asset types, brush types, scan folders, icon map
│   ├── ipc.py                # File-based IPC writer
│   ├── theme.py              # Dark theme QSS stylesheet (~450 lines)
│   ├── settings.py           # JSON-backed persistent app settings (AppSettings)
│   ├── settings_dialog.py    # Settings dialog with category sidebar
│   ├── setup_dialog.py       # First-run setup wizard (ZBrush path selection)
│   ├── zbrush_detect.py      # Auto-detect ZBrush installs (registry + Program Files)
│   ├── zbp_thumbnail.py      # ZBP thumbnail extractor (port of Pixologic algorithm)
│   ├── brush_scanner.py      # Scans ZBrush dirs for .ZBP files, caches thumbnails
│   ├── brush_grid.py         # QListWidget in icon mode — thumbnail grid with search
│   ├── icons/                # Flat-style SVG panel/tab icons (20×20 viewBox, 32×32 size)
│   │   ├── brushes.svg … documents.svg  (13 asset-type icons)
│   │   ├── favorites.svg
│   │   └── metadata.svg
│   └── data/                 # Runtime data (created at runtime, not committed)
│       ├── brush_metadata.json    # User metadata store
│       ├── brush_cache.json       # Scan index cache
│       ├── thumbnails/            # Cached .rgba thumbnail files (96×96)
│       ├── settings.json          # Persistent app settings
│       └── ipc/                   # IPC command files
├── zbrush_plugin/            # ZBrush-side bridge
│   └── xmd_bridge.py         # Reads IPC commands, executes SDK calls
├── xmd_toolbox/              # (Legacy) In-ZBrush plugin code — may be removed
├── docs/
│   ├── plugin-plan.md        # THIS FILE — project source of truth
│   ├── copilot-instructions.md
│   └── zbrush-2026-1-api.md
├── .venv/                    # Python 3.11.9 venv (not committed)
├── requirements.txt
└── README.md
```

## Dependencies

```
PySide6>=6.10
PySide6-QtAds>=4.5
```

## Product Scope (Core)

- Organize all ZBrush assets.
- Add metadata per asset (description, tags, categories, author, and more).
- Search across assets.
- Create favorites (e.g., starred items in a favorites view).
- Each asset type has its own interface section.
- UI should support multi-monitor workflows via dockable/tearable panels.
- Professional dark-mode UI inspired by DCC tooling.

---

## UI Implementation Status

### Docking System (QtAds) — DONE

- **PySide6-QtAds** (`CDockManager`) as the central widget.
- Config flags: `DockAreaHasUndockButton`, `AlwaysShowTabs`, `FocusHighlighting`,
  `EqualSplitOnInsertion`, `OpaqueSplitterResize`.
- All panels are tearable, dockable, and re-tabbable.
- Floating containers styled to match the dark theme.

### Dark Theme — DONE

- Comprehensive QSS in `app/theme.py` (~450 lines).
- Surface hierarchy: `#121214` (base) → `#1C1C1E` (surface) → `#252528` (raised)
  → `#2E2E32` (hover) → `#38383D` (pressed).
- Text: primary `#E0E0E0`, secondary `#9A9A9E`, disabled `#555558`.
- Accent: warm orange `#E8652B` with hover/pressed variants.
- Full QtAds overrides: `CDockContainerWidget`, `CDockAreaWidget`,
  `CDockWidgetTab`, `CDockAreaTitleBar`, `CFloatingDockContainer`, `CDockSplitter`.
- Styled: buttons (including accent/checked), inputs, comboboxes, group boxes,
  list/tree/table views, scrollbars, splitters, tooltips, status bar, form labels.

### Tab Icons — DONE

- 15 flat-style SVG icons (20×20, stroke-based, `#9A9A9E` secondary color).
- All 13 asset-type tabs + Favorites + Metadata panels have icons.
- Icon mapping centralized in `config.py` → `TAB_ICONS`.
- Icons loaded via `_icon_for()` helper with in-memory cache.
- `qproperty-iconSize: 20px 20px` set on dock widget tabs via QSS.
- Icon filenames: `{asset_type_snake_case}.svg` (e.g., `array_mesh.svg`).

### Panels — PARTIAL

| Panel | Status | Notes |
|-------|--------|-------|
| Brushes | **Done** | Grid view with 96×96 thumbnails extracted from .ZBP files. Search filter + favorites toggle. Scans ZBrush install dirs on startup. Deduplicates by name across ZBrushes/ZData/ZStartup folders. |
| Metadata | **Done** | Form: description, type dropdown, category, tags, author, favorite toggle, save. Populates on brush grid selection. |
| Favorites | **Done** | Shortlist, double-click to jump to brush metadata. |
| Alphas | Stubbed | "Coming soon" placeholder |
| Textures | Stubbed | "Coming soon" placeholder |
| Materials | Stubbed | "Coming soon" placeholder |
| Fibers | Stubbed | "Coming soon" placeholder |
| Tools | Stubbed | "Coming soon" placeholder |
| Lights | Stubbed | "Coming soon" placeholder |
| Projects | Stubbed | "Coming soon" placeholder |
| Grids | Stubbed | "Coming soon" placeholder |
| Array Mesh | Stubbed | "Coming soon" placeholder |
| Spotlights | Stubbed | "Coming soon" placeholder |
| Render Presets | Stubbed | "Coming soon" placeholder |
| Documents | Stubbed | "Coming soon" placeholder |

### Settings System — DONE

- **AppSettings** (`settings.py`): JSON-backed persistent settings with auto-save.
  Properties for `zbrush_path`, `first_run_complete`, and all UI prefs.
- **SetupDialog** (`setup_dialog.py`): First-run wizard shown before main window.
  Lists auto-detected ZBrush installs or lets user browse manually.
  Blocks until user completes setup or cancels (exits app).
- **SettingsDialog** (`settings_dialog.py`): Full settings dialog opened from toolbar.
  Category sidebar with General page + per-asset-type pages.
  General page has: Options checkboxes, ZBrush Path with browse + auto-detect,
  Advanced Options (Import/Export DB, Rescan).
- **ZBrush auto-detect** (`zbrush_detect.py`): Scans Windows registry
  (`HKLM/HKCU` under `Maxon` and `Pixologic` keys) and `Program Files` directories.
  Returns sorted list newest-first.
- `main.py` checks `first_run_complete` — if false, shows SetupDialog before main window.
- Settings button in toolbar opens SettingsDialog.

### ZBP Thumbnail Extraction — DONE

- **zbp_thumbnail.py**: Port of Pixologic's `ReadZBrushFileThumbnail` (by Ofer Alon).
  Searches for magic pattern `00 90 00 00 04 00 80 01` starting 200 bytes into the file.
  Handles compression version 4 (4× 2-byte block sizes) and v5+ (12-byte skip + 2× 4-byte).
  RLE decompression: positive byte = repeat, negative = literal run, 0 = end sentinel.
  v6+ has extra 4-byte skip per block.
  Decompressed data is planar: interleaved into 4 sub-channels per block.
  R↔B swap happens inline during alpha channel write (same as C++ code).
  Alpha is optionally boosted (squared * 0.5, capped at 255) for dark-background icons.
  Output: 96×96 RGBA, 36 864 bytes. Saved as raw `.rgba` files in `app/data/thumbnails/`.

### Brush Scanner — DONE

- **brush_scanner.py**: Scans `ZBrushes`, `ZData/BrushPresets`, and
  `ZStartup/BrushPresets` subdirectories of the configured ZBrush install path.
  Deduplicates by brush name (first occurrence wins — ZBrushes scanned first).
  Extracts thumbnails via `zbp_thumbnail.py` and caches as `.rgba` files.
  Maintains a JSON cache (`brush_cache.json`) keyed by file path + mtime.
  Subsequent launches skip extraction for unchanged files.
  Category is derived from the immediate parent folder name.

### Brush Grid — DONE

- **brush_grid.py**: `BrushGridWidget` wrapping a `QListWidget` in `IconMode`.
  72×72 display size, 96×96 source thumbnails scaled with smooth transformation.
  Consistent label positioning at bottom of each cell (placeholder pixmap for missing thumbs).
  Search input filters by name substring. Favorites toggle button.
  Emits `brush_selected(name, path)` signal on click.
  In-memory pixmap cache for loaded thumbnails.

### Toolbar — DONE

- "About" action — opens about dialog.
- "Panels" dropdown — per-panel checkable visibility toggles.
- "Settings" button — opens SettingsDialog.
- "Reset Layout" button — restores default dock layout.

### Data Layer — DONE (local dev)

- `BrushMetadata` dataclass with `to_dict()` / `from_dict()`.
- `LocalStore` — JSON-file-backed CRUD with search and favorites.
- Path: `app/data/brush_metadata.json`.

### IPC — PLACEHOLDER

- `ipc.py` writes timestamped JSON command files to `app/data/ipc/`.
- Write-only; no response/acknowledgment mechanism.
- Protocol not finalized.

---

## Not Yet Implemented

| Feature | Priority | Notes |
|---------|----------|-------|
| IPC protocol finalization | High | Define command schema, add response handling, test with bridge |
| Activate brush in ZBrush | High | Send selected brush path via IPC to bridge plugin |
| Non-Brush asset models | Medium | Only `BrushMetadata` exists; need generic asset model |
| Alpha/Texture/Material scanning | Medium | Reuse scanner pattern with different extensions/thumbnail logic |
| Brush type auto-detection | Medium | Parse ZBP data to determine brush type (Standard, Clay, Insert, etc.) |
| Grid label truncation polish | Low | Long names get elided; could show full name on hover |
| Async scanning with progress bar | Low | Current scan blocks UI briefly on first run (~2s for 200 brushes) |
| S3 storage backend | Low | Deferred until metadata schema stabilizes |
| ZBrush bridge plugin testing | Low | `xmd_bridge.py` exists but untested with 2026.1 |

## Completed

| Feature | Date | Notes |
|---------|------|-------|
| Dark theme & docking | 2026-02-11 | QtAds panels, QSS dark theme, SVG tab icons |
| Panel visibility toggle | 2026-02-11 | Toolbar "Panels" dropdown with per-panel checkable actions |
| Dock layout persistence | 2026-02-11 | Auto-save on close, restore on launch, Reset toolbar button |
| Settings system | 2026-02-11 | AppSettings (JSON), SettingsDialog, first-run SetupDialog |
| ZBrush auto-detect | 2026-02-11 | Registry + Program Files scan, sorted newest-first |
| ZBP thumbnail extraction | 2026-02-11 | Port of Pixologic ReadZBrushFileThumbnail algorithm |
| Brush directory scanning | 2026-02-11 | Recursive scan with mtime-based caching and dedup |
| Brush grid view | 2026-02-11 | QListWidget icon mode, 72px thumbnails, search + favorites |

---

## Open Questions

- Socket-based IPC feasibility (requires confirming threading in ZBrush VM).
- Favorites storage scope (global vs. per user/project).
- Brush type auto-detection — can brush type be parsed from ZBP binary data?
- Whether to show brush category (folder name) as a filterable field in the grid.

## Resolved Decisions

- External PySide6 app replaces in-ZBrush UI for richer controls.
- Python 3.11.9 in a project-local venv (do not replace system Python).
- File-based IPC (JSON command files) for ZBrush communication.
- v1 asset type focus: Brushes only. All other tabs are present but stubbed.
- Asset types with tabs: Brushes, Alphas, Textures, Materials, Fibers, Tools, Lights,
  Projects, Grids, Array Mesh, Spotlights, Render Presets, Documents.
- Metadata schema for brushes: name, description, brush_type (dropdown), category,
  tags, author, favorite, file_path, scan_date.
- Brush identification: by name. Brush directory path is configurable.
- Brush directory scanning: ZBrushes scanned first, ZData/ZStartup also scanned.
  `ZStartup/BrushPresets` was the brush preset location before ZBrush 2026.1.
  `ZData/BrushPresets` is the location for ZBrush 2026.1+.
  Deduplication is by brush name (first occurrence wins).
- Thumbnail extraction: Port of Pixologic's C++ `ReadZBrushFileThumbnail`.
  Icons saved as raw `.rgba` 96×96 files for fastest load (no PNG encode/decode).
  Cached on disk with mtime-based invalidation.
- Grid display: QListWidget in IconMode (not a custom painter). 72px display size.
  Labels truncated with Qt text elide. Full name shown in tooltip.
- Storage: S3 is planned but deferred. Local JSON file store used during development.
- Brush type taxonomy: 46 types defined in `config.py`.
- File extensions per asset type defined in `config.py` for directory scanning.
- Tab icons: flat-style SVG icons replace text-only tab labels on dock widgets.
- Dark theme: professional charcoal surface hierarchy with warm orange accent.
- Docking: QtAds provides tear-off, undock, retab, and float support.
- PySide6 `Fusion` style used as the dark-mode foundation.

## Dependency Strategy

- Prefer local dependencies in a libs/ folder with isolated sys.path changes.
- Remove added paths after importing.
- Use unique module names if a simple approach is used.

## Storage Strategy

- Production: AWS S3 (deferred until metadata schema stabilizes).
- Development: local JSON file at app/data/brush_metadata.json.
- LocalStore in app/local_store.py implements file-backed read/write with search and favorites.
- StorageBackend protocol in xmd_toolbox/storage.py for future S3/other backends.

## Error Handling

- Validate item paths with exists() before operations.
- Use defensive checks for active tool/subtool state.
- Keep UI updates minimal; use freeze() for heavy operations.

## Testing Approach

- Smoke tests via ZBrush scripting console.
- Script-level tests using recorded macros for repeatable UI state.
- Manual validation in ZBrush 2026.1.

## Risks and Mitigations

- Shared interpreter state can cause conflicts.
  - Mitigation: minimize globals and clean up sys.path.
- GUI-dependent actions can break if UI state changes.
  - Mitigation: use config(2026) or explicit state checks.
- Limited modeling API access.
  - Mitigation: rely on UI actions and available queries.

---

## Current State Summary (for AI handoff)

**What works right now:**
The app launches, shows a first-run setup dialog if no ZBrush path is configured,
auto-detects ZBrush installations, then opens the main window with a dockable panel
layout. The Brushes tab shows a grid of ~216 brush thumbnails extracted directly from
`.ZBP` files using a port of Pixologic's C++ algorithm. Search and favorites filtering
work. Clicking a brush populates the Metadata panel form. Settings persist to JSON.
Layout state persists across launches.

**How to run:**
```
cd D:\Perforce\_APPS_Python\XMDToolBox
.venv\Scripts\python.exe app/main.py
```

**Key technical details an AI needs to know:**
1. ZBP thumbnails use a block-compressed planar format with a magic byte scan.
   The algorithm is in `app/zbp_thumbnail.py` — do NOT try to rewrite this casually.
   It was painstakingly reverse-engineered from C++ source in the old ToolBox 4.0
   repo (`mdunnam/XMDToolBox4.0`, branch `trunk`, file `Util/brushiconimageprovider.cpp`).
2. Thumbnails are cached as raw `.rgba` files (not PNG) in `app/data/thumbnails/`.
   A JSON cache index at `app/data/brush_cache.json` tracks mtime for invalidation.
3. Brushes are deduplicated by name across scan directories. `ZBrushes` folder is
   scanned first and wins on name collision.
4. The old C++/Qt ToolBox 4.0 repo at `mdunnam/XMDToolBox4.0` has working reference
   implementations for all resource types. Use `github_repo` tool to search it.
5. The `xmd_toolbox/` directory is legacy code from an earlier ZScript-based approach.
   It may be removed. The active code is in `app/` and `zbrush_plugin/`.
6. ZBrush 2026.1 changed the brush preset location from `ZStartup/BrushPresets` to
   `ZData/BrushPresets`. The scanner checks both.

**What to work on next (in priority order):**
1. Polish the brush grid — consider showing category grouping or folder headers.
2. Wire IPC: clicking a brush should send its path to ZBrush via the bridge plugin.
3. Implement alpha/texture scanning (different file formats, no ZBP extraction needed).
4. Add brush type auto-detection from ZBP binary data (if possible).
5. Test `xmd_bridge.py` inside ZBrush 2026.1.
