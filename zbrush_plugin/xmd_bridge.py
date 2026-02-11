"""XMD ToolBox bridge plugin for ZBrush.

This lightweight script runs inside ZBrush's embedded Python 3.11.9 interpreter.
It reads JSON command files written by the external PySide6 app and executes them
via the ZBrush Python SDK (zbrush.commands).

Placeholder. IPC protocol is not finalized yet.

Usage:
    Load via ZScript > Python Scripting > Load, or install via ZBRUSH_PLUGIN_PATH.
"""

from __future__ import annotations

import json
import os
import glob

from zbrush import commands as zbc


# --- Configuration ---

# Directory where the external app writes command files.
# Must match app/config.py IPC_DIR.  Adjust if needed.
_SCRIPT_DIR: str = os.path.dirname(os.path.abspath(__file__))
_IPC_DIR: str = os.path.join(_SCRIPT_DIR, "..", "app", "data", "ipc")


def _read_commands() -> list[dict]:
    """Read and delete all pending command files from the IPC directory.

    Returns:
        A list of parsed command dicts.
    """
    if not os.path.isdir(_IPC_DIR):
        return []

    commands: list[dict] = []
    for filepath in sorted(glob.glob(os.path.join(_IPC_DIR, "cmd_*.json"))):
        try:
            with open(filepath, "r", encoding="utf-8") as fh:
                commands.append(json.load(fh))
            os.remove(filepath)
        except (json.JSONDecodeError, OSError):
            pass
    return commands


def _execute(cmd: dict) -> None:
    """Execute a single command dict.

    Placeholder. Only "set_brush" is partially supported as a proof of concept.

    Args:
        cmd: The command dict with "command" and "payload" keys.
    """
    name = cmd.get("command", "")
    payload = cmd.get("payload", {})

    if name == "set_brush":
        brush_name = payload.get("name", "")
        item_path = f"Brush:{brush_name}"
        if zbc.exists(item_path):
            zbc.press(item_path)
            print(f"[XMD Bridge] Activated brush: {brush_name}")
        else:
            print(f"[XMD Bridge] Brush not found: {brush_name}")
    else:
        # Placeholder: unknown commands are logged but not executed.
        print(f"[XMD Bridge] Unknown command: {name}")


def poll() -> None:
    """Read and execute all pending IPC commands.

    Call this manually or bind it to a palette button so the user can
    trigger it at will.
    """
    commands = _read_commands()
    for cmd in commands:
        _execute(cmd)
    if commands:
        print(f"[XMD Bridge] Processed {len(commands)} command(s).")


# --- ZBrush UI setup ---

def _setup_ui() -> None:
    """Register a palette button in ZBrush so the user can poll for commands."""
    palette = "XMD Bridge"
    if not zbc.exists(palette):
        zbc.add_palette(palette)
    btn_path = f"{palette}:Poll Commands"
    if not zbc.exists(btn_path):
        zbc.add_button(btn_path, "Read pending commands from XMD ToolBox", _on_poll)


def _on_poll(sender: str) -> None:
    """Button callback that triggers command polling.

    Args:
        sender: The item path of the button.
    """
    poll()


# Auto-setup when loaded.
_setup_ui()
