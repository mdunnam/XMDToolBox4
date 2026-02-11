"""Entry point for the XMD ToolBox external application.

Run this file to launch the PySide6 desktop app:

    .venv/Scripts/python.exe app/main.py
"""

from __future__ import annotations

import os
import sys

# Ensure the project root is on sys.path so `app` is importable as a package.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from PySide6.QtWidgets import QApplication

from app.main_window import MainWindow
from app.settings import AppSettings
from app.setup_dialog import SetupDialog
from app.theme import STYLESHEET


def main() -> None:
    """Create the application, show the main window, and enter the event loop."""
    app = QApplication(sys.argv)
    app.setApplicationName("XMD ToolBox")
    app.setStyle("Fusion")  # Fusion base gives the best dark-mode foundation.
    app.setStyleSheet(STYLESHEET)

    settings = AppSettings()

    # First-run setup — show before the main window.
    if not settings.first_run_complete:
        dlg = SetupDialog(settings)
        if dlg.exec() == SetupDialog.DialogCode.Rejected:
            sys.exit(0)

    window = MainWindow(settings=settings)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
