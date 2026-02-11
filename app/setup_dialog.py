"""First-run setup dialog for XMD ToolBox.

Shown once on first launch.  Lets the user pick a detected ZBrush
installation or manually browse to one, then marks setup as complete.
Mirrors the workflow from the v3 installer screenshot.
"""

from __future__ import annotations

import os

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QRadioButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .settings import AppSettings
from .zbrush_detect import ZBrushInstall, detect_zbrush_installs


class SetupDialog(QDialog):
    """First-run setup wizard that detects ZBrush and lets the user choose.

    The dialog blocks the main window until the user either completes
    setup or cancels.
    """

    def __init__(self, settings: AppSettings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._settings = settings
        self._detected: list[ZBrushInstall] = []

        self.setWindowTitle("XMD ToolBox — Setup")
        self.setMinimumSize(700, 520)
        self.setModal(True)

        self._build_ui()
        self._run_detection()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Construct the dialog layout."""
        root = QHBoxLayout(self)
        root.setSpacing(20)
        root.setContentsMargins(24, 24, 24, 24)

        # ---- Left column: welcome text ----
        left = QVBoxLayout()
        left.setSpacing(16)

        welcome = QLabel("Welcome to XMD ToolBox")
        welcome.setProperty("heading", True)
        left.addWidget(welcome)

        instructions = QLabel(
            "1.  Select your ZBrush version or manually enter the\n"
            "    installation location.\n"
            "2.  Click <b>Complete Setup</b>."
        )
        instructions.setWordWrap(True)
        instructions.setProperty("secondary", True)
        left.addWidget(instructions)
        left.addStretch()

        root.addLayout(left, 1)

        # ---- Right column: detection + path input ----
        right = QVBoxLayout()
        right.setSpacing(16)

        # Auto-detected list
        self._detect_radio = QRadioButton("Detected ZBrush Versions")
        self._detect_radio.setChecked(True)
        self._detect_radio.toggled.connect(self._on_radio_toggled)
        right.addWidget(self._detect_radio)

        self._detect_list = QListWidget()
        self._detect_list.setMinimumHeight(120)
        self._detect_list.currentItemChanged.connect(self._on_detection_selected)
        right.addWidget(self._detect_list)

        # Manual path
        self._manual_radio = QRadioButton("Select ZBrush Path")
        self._manual_radio.toggled.connect(self._on_radio_toggled)
        right.addWidget(self._manual_radio)

        path_row = QHBoxLayout()
        path_row.setSpacing(8)
        self._path_input = QLineEdit()
        self._path_input.setPlaceholderText("C:\\Program Files\\Maxon ZBrush 2026")
        self._path_input.setEnabled(False)
        path_row.addWidget(self._path_input)

        self._browse_btn = QPushButton("Browse…")
        self._browse_btn.setFixedWidth(90)
        self._browse_btn.setEnabled(False)
        self._browse_btn.clicked.connect(self._on_browse)
        path_row.addWidget(self._browse_btn)
        right.addLayout(path_row)

        # Status log
        log_group = QGroupBox("Setup Log")
        log_layout = QVBoxLayout(log_group)
        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setMaximumHeight(100)
        log_layout.addWidget(self._log)
        right.addWidget(log_group)

        # Complete button
        self._complete_btn = QPushButton("Complete Setup")
        self._complete_btn.setProperty("accent", True)
        self._complete_btn.setEnabled(False)
        self._complete_btn.clicked.connect(self._on_complete)
        right.addWidget(self._complete_btn)

        root.addLayout(right, 2)

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    def _run_detection(self) -> None:
        """Scan for ZBrush installations and populate the list."""
        self._log_message("Scanning for ZBrush installations…")
        self._detected = detect_zbrush_installs()

        self._detect_list.clear()
        if self._detected:
            for inst in self._detected:
                label = f"ZBrush {inst.version}:  {inst.path}"
                item = QListWidgetItem(label)
                item.setData(Qt.ItemDataRole.UserRole, inst.path)
                self._detect_list.addItem(item)
            self._detect_list.setCurrentRow(0)
            self._log_message(f"Found {len(self._detected)} installation(s).")
        else:
            self._log_message("No ZBrush installations detected.")
            self._log_message("Use 'Select ZBrush Path' to set one manually.")
            self._manual_radio.setChecked(True)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    @Slot()
    def _on_radio_toggled(self) -> None:
        """Enable/disable controls based on which radio is selected."""
        manual = self._manual_radio.isChecked()
        self._detect_list.setEnabled(not manual)
        self._path_input.setEnabled(manual)
        self._browse_btn.setEnabled(manual)
        self._update_complete_enabled()

    @Slot()
    def _on_detection_selected(self) -> None:
        """Handle selection in the detected-versions list."""
        self._update_complete_enabled()

    @Slot()
    def _on_browse(self) -> None:
        """Open a folder picker for the ZBrush install directory."""
        folder = QFileDialog.getExistingDirectory(
            self, "Select ZBrush Install Directory"
        )
        if folder:
            self._path_input.setText(folder)
            self._update_complete_enabled()

    @Slot()
    def _on_complete(self) -> None:
        """Save the chosen path and close the dialog."""
        path = self._selected_path()
        if not path:
            return
        self._settings.zbrush_path = path
        self._settings.first_run_complete = True
        self._log_message(f"ZBrush path set to: {path}")
        self._log_message("Setup complete!")
        self.accept()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _selected_path(self) -> str:
        """Return the currently selected ZBrush path.

        Returns:
            The path string, or empty if none selected.
        """
        if self._manual_radio.isChecked():
            return self._path_input.text().strip()
        item = self._detect_list.currentItem()
        if item is None:
            return ""
        return item.data(Qt.ItemDataRole.UserRole) or ""

    def _update_complete_enabled(self) -> None:
        """Enable the 'Complete' button only if a valid path is chosen."""
        path = self._selected_path()
        self._complete_btn.setEnabled(bool(path) and os.path.isdir(path))

    def _log_message(self, text: str) -> None:
        """Append a line to the setup log.

        Args:
            text: The message to display.
        """
        self._log.append(text)
