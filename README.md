# XMD ToolBox

Asset organizer for ZBrush 2026.1 (and planned multi-DCC support).

## Project Structure

```
XMDToolBox/
├── app/                    # External PySide6 desktop application
│   ├── __init__.py
│   ├── main.py             # Entry point — run this to launch the app
│   ├── main_window.py      # Main window and tab container
│   ├── models.py           # Data models (BrushMetadata, etc.)
│   ├── local_store.py      # Local JSON metadata store (dev)
│   ├── config.py           # Constants, asset types, brush types
│   └── ipc.py              # File-based IPC with ZBrush
├── zbrush_plugin/          # Lightweight ZBrush-side plugin (reads IPC commands)
│   ├── xmd_bridge.py       # ZBrush Python SDK bridge (polls command files)
│   └── xmd_commands.txt    # ZScript fallback (future)
├── docs/                   # Documentation
├── .venv/                  # Python 3.11.9 virtual environment (not committed)
├── requirements.txt
└── README.md
```

## Setup

1. **Python 3.11.9** is required. Install it alongside your system Python (do not replace it).
2. Create a venv in the project root:
   ```
   py -3.11 -m venv .venv
   ```
3. Activate and install dependencies:
   ```
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. Run the app:
   ```
   python app/main.py
   ```

## ZBrush Integration

The external app communicates with ZBrush via file-based IPC:
- The app writes command files to a known directory.
- A lightweight ZBrush plugin reads and executes them.

See `docs/plugin-plan.md` for architecture details.
