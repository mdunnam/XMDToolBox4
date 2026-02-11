"""File-based IPC for communicating with ZBrush.

The external app writes JSON command files to a shared directory.
A lightweight ZBrush plugin polls that directory and executes commands.

Placeholder module. IPC protocol is not finalized yet.
"""

from __future__ import annotations

import json
import os
import time

from .config import IPC_DIR


def _ensure_ipc_dir() -> None:
    """Create the IPC directory if it does not exist."""
    os.makedirs(IPC_DIR, exist_ok=True)


def send_command(command: str, payload: dict | None = None) -> None:
    """Write a command file for ZBrush to pick up.

    Placeholder. Command protocol is not finalized yet.

    Args:
        command: The command name (e.g. "set_brush").
        payload: Optional dict of command arguments.
    """
    _ensure_ipc_dir()
    data = {
        "command": command,
        "payload": payload or {},
        "timestamp": time.time(),
    }
    filename = f"cmd_{int(time.time() * 1000)}.json"
    filepath = os.path.join(IPC_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False)
