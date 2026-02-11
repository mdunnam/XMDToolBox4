"""Settings dialog for XMD ToolBox.

Category list on the left, stacked setting pages on the right —
matching the layout from the v3 settings screenshot.
"""

from __future__ import annotations

import os

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .config import ASSET_TABS
from .settings import AppSettings
from .zbrush_detect import detect_zbrush_installs


class SettingsDialog(QDialog):
    """Modal settings dialog with a category sidebar and page stack.

    Categories correspond to the v3 layout: General, per-asset-type,
    and advanced options.
    """

    def __init__(self, settings: AppSettings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._settings = settings

        self.setWindowTitle("Settings")
        self.setMinimumSize(780, 560)
        self.setModal(True)

        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Construct the dialog layout."""
        root = QHBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # ---- Left: category list ----
        self._cat_list = QListWidget()
        self._cat_list.setFixedWidth(180)
        self._cat_list.setSpacing(2)
        self._cat_list.currentRowChanged.connect(self._on_category_changed)
        root.addWidget(self._cat_list)

        # ---- Right: stacked pages ----
        right = QVBoxLayout()
        right.setContentsMargins(20, 20, 20, 20)
        right.setSpacing(16)

        self._stack = QStackedWidget()
        right.addWidget(self._stack, 1)

        # Close button
        close_row = QHBoxLayout()
        close_row.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(self.accept)
        close_row.addWidget(close_btn)
        right.addLayout(close_row)

        root.addLayout(right, 1)

        # ---- Populate categories & pages ----
        self._add_general_page()
        for tab in ASSET_TABS:
            self._add_asset_page(tab)

        self._cat_list.setCurrentRow(0)

    # ------------------------------------------------------------------
    # General page
    # ------------------------------------------------------------------

    def _add_general_page(self) -> None:
        """Build the 'General' settings page."""
        self._cat_list.addItem("General")

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)

        # --- Options group ---
        options_group = QGroupBox("Options")
        opts = QVBoxLayout(options_group)
        opts.setSpacing(12)

        self._chk_single_click = QCheckBox("Single-click Select")
        self._chk_single_click.setChecked(
            self._settings.get("single_click_select", False)
        )
        self._chk_single_click.toggled.connect(
            lambda v: self._settings.set("single_click_select", v)
        )
        opts.addWidget(self._chk_single_click)

        self._chk_tooltips = QCheckBox("Show Advanced Tooltips")
        self._chk_tooltips.setChecked(
            self._settings.get("show_advanced_tooltips", True)
        )
        self._chk_tooltips.toggled.connect(
            lambda v: self._settings.set("show_advanced_tooltips", v)
        )
        opts.addWidget(self._chk_tooltips)

        self._chk_category = QCheckBox("Show XMD Category")
        self._chk_category.setChecked(
            self._settings.get("show_xmd_category", True)
        )
        self._chk_category.toggled.connect(
            lambda v: self._settings.set("show_xmd_category", v)
        )
        opts.addWidget(self._chk_category)

        self._chk_auto_update = QCheckBox("Automatically Update ToolBox")
        self._chk_auto_update.setChecked(
            self._settings.get("auto_update", True)
        )
        self._chk_auto_update.toggled.connect(
            lambda v: self._settings.set("auto_update", v)
        )
        opts.addWidget(self._chk_auto_update)

        layout.addWidget(options_group)

        # --- ZBrush Path group ---
        path_group = QGroupBox("ZBrush Path")
        path_layout = QVBoxLayout(path_group)
        path_layout.setSpacing(12)

        path_row = QHBoxLayout()
        path_row.setSpacing(8)
        self._zbrush_path_input = QLineEdit()
        self._zbrush_path_input.setText(self._settings.zbrush_path)
        self._zbrush_path_input.setPlaceholderText(
            "C:\\Program Files\\Maxon ZBrush 2026"
        )
        self._zbrush_path_input.editingFinished.connect(self._on_path_edited)
        path_row.addWidget(self._zbrush_path_input)

        browse_btn = QPushButton("Browse…")
        browse_btn.setFixedWidth(90)
        browse_btn.clicked.connect(self._on_browse_zbrush)
        path_row.addWidget(browse_btn)

        detect_btn = QPushButton("Auto-Detect")
        detect_btn.setFixedWidth(100)
        detect_btn.clicked.connect(self._on_auto_detect)
        path_row.addWidget(detect_btn)

        path_layout.addLayout(path_row)

        self._path_status = QLabel("")
        self._path_status.setProperty("secondary", True)
        self._update_path_status()
        path_layout.addWidget(self._path_status)

        layout.addWidget(path_group)

        # --- Advanced Options group ---
        adv_group = QGroupBox("Advanced Options")
        adv = QVBoxLayout(adv_group)
        adv.setSpacing(12)

        import_btn = QPushButton("Import Database")
        import_btn.clicked.connect(self._on_import_db)
        adv.addWidget(import_btn)

        export_btn = QPushButton("Export Database")
        export_btn.clicked.connect(self._on_export_db)
        adv.addWidget(export_btn)

        rescan_btn = QPushButton("Rescan Local Files")
        rescan_btn.clicked.connect(self._on_rescan)
        adv.addWidget(rescan_btn)

        layout.addWidget(adv_group)

        layout.addStretch()

        # Wrap in scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(page)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._stack.addWidget(scroll)

    # ------------------------------------------------------------------
    # Per-asset placeholder pages
    # ------------------------------------------------------------------

    def _add_asset_page(self, name: str) -> None:
        """Add a placeholder settings page for an asset type.

        Args:
            name: The asset type display name.
        """
        self._cat_list.addItem(name)

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)

        heading = QLabel(f"{name} Settings")
        heading.setProperty("heading", True)
        layout.addWidget(heading)

        placeholder = QLabel("Settings for this asset type will appear here.")
        placeholder.setProperty("secondary", True)
        layout.addWidget(placeholder)

        layout.addStretch()
        self._stack.addWidget(page)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    @Slot(int)
    def _on_category_changed(self, row: int) -> None:
        """Switch the visible settings page.

        Args:
            row: The selected category index.
        """
        self._stack.setCurrentIndex(row)

    @Slot()
    def _on_path_edited(self) -> None:
        """Save the manually typed ZBrush path."""
        path = self._zbrush_path_input.text().strip()
        self._settings.zbrush_path = path
        self._update_path_status()

    @Slot()
    def _on_browse_zbrush(self) -> None:
        """Open a folder picker for the ZBrush directory."""
        start = self._settings.zbrush_path or ""
        folder = QFileDialog.getExistingDirectory(
            self, "Select ZBrush Install Directory", start
        )
        if folder:
            self._zbrush_path_input.setText(folder)
            self._settings.zbrush_path = folder
            self._update_path_status()

    @Slot()
    def _on_auto_detect(self) -> None:
        """Run auto-detection and fill in the first result."""
        installs = detect_zbrush_installs()
        if installs:
            best = installs[0]
            self._zbrush_path_input.setText(best.path)
            self._settings.zbrush_path = best.path
            self._path_status.setText(
                f"Detected ZBrush {best.version} at {best.path}"
            )
        else:
            self._path_status.setText("No ZBrush installations found.")

    @Slot()
    def _on_import_db(self) -> None:
        """Import a metadata database file (placeholder)."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Database", "", "JSON Files (*.json)"
        )
        if path:
            # TODO: implement actual import logic
            pass

    @Slot()
    def _on_export_db(self) -> None:
        """Export the metadata database (placeholder)."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Database", "xmd_metadata.json", "JSON Files (*.json)"
        )
        if path:
            # TODO: implement actual export logic
            pass

    @Slot()
    def _on_rescan(self) -> None:
        """Trigger a full rescan of local brush files (placeholder)."""
        # TODO: implement scan logic once brush scanner is built
        pass

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _update_path_status(self) -> None:
        """Update the status label below the ZBrush path input."""
        path = self._settings.zbrush_path
        if not path:
            self._path_status.setText("No ZBrush path configured.")
        elif os.path.isdir(path):
            self._path_status.setText(f"✓  {path}")
        else:
            self._path_status.setText(f"⚠  Directory not found: {path}")
