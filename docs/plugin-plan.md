# XMD ToolBox Plan (ZBrush 2026.1)

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
│   ├── main.py               # Entry point
│   ├── main_window.py        # Main window with dockable panels
│   ├── models.py             # Data models (BrushMetadata)
│   ├── local_store.py        # Local JSON metadata store (dev)
│   ├── config.py             # Constants, asset types, brush types, icon map
│   ├── ipc.py                # File-based IPC writer
│   ├── theme.py              # Dark theme QSS stylesheet
│   ├── icons/                # Flat-style SVG panel/tab icons (20×20, stroke)
│   │   ├── brushes.svg
│   │   ├── alphas.svg
│   │   ├── textures.svg
│   │   ├── materials.svg
│   │   ├── fibers.svg
│   │   ├── tools.svg
│   │   ├── lights.svg
│   │   ├── projects.svg
│   │   ├── grids.svg
│   │   ├── array_mesh.svg
│   │   ├── spotlights.svg
│   │   ├── render_presets.svg
│   │   ├── documents.svg
│   │   ├── favorites.svg
│   │   └── metadata.svg
│   └── data/                 # Runtime data (JSON metadata, IPC dir)
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
| Brushes | **Done** | List + search + favorites filter, center area |
| Metadata | **Done** | Form: description, type dropdown, category, tags, author, favorite toggle, save |
| Favorites | **Done** | Shortlist, double-click to jump to brush |
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

### Toolbar — PARTIAL

- "About" action — opens about dialog. **Done.**
- "Panels" action — exists but **not wired** to toggle panel visibility.

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
| Settings / Preferences UI | Medium | ZBrush install path config, user preferences |
| Non-Brush asset models | Medium | Only `BrushMetadata` exists; need generic asset model |
| Brush directory scanning | Medium | Scan ZBrush folders and populate store |
| IPC protocol finalization | Medium | Define command schema, add response handling |
| S3 storage backend | Low | Deferred until metadata schema stabilizes |

## Completed

| Feature | Date | Notes |
|---------|------|-------|
| Panel visibility toggle | 2026-02-11 | Toolbar "Panels" dropdown menu with per-panel checkable actions |
| Dock layout persistence | 2026-02-11 | Auto-save on close, restore on launch, Save/Reset toolbar buttons |

---

## Open Questions

- Socket-based IPC feasibility (requires confirming threading in ZBrush VM).
- Brush directory scanning UX (manual trigger vs. file watchers).
- Favorites storage scope (global vs. per user/project).

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
