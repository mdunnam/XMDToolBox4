"""Main window for XMD ToolBox.

Professional dark-mode application with dockable, tearable panels.
Uses Qt Advanced Docking System (QtAds) for DCC-style panel management.
Only the Brushes panel has functional content; all others show a placeholder.
"""

from __future__ import annotations

import os

from PySide6.QtCore import Qt, Slot, QSize, QByteArray, QTimer
from PySide6.QtGui import QAction, QFont, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QStatusBar,
    QTextEdit,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
import PySide6QtAds as ads

from .config import (
    APP_NAME,
    APP_VERSION,
    ASSET_TABS,
    BRUSH_TYPES,
    ICONS_DIR,
    LAYOUT_STATE_PATH,
    LOCAL_METADATA_PATH,
    TAB_ICONS,
)
from .brush_grid import BrushGridWidget
from .brush_scanner import scan_brush_directories
from .local_store import LocalStore
from .models import BrushMetadata
from .settings import AppSettings
from .settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    """Top-level application window with dockable panels."""

    def __init__(self, settings: AppSettings | None = None) -> None:
        super().__init__()
        self.setWindowTitle(f"{APP_NAME}  {APP_VERSION}")
        self.resize(1400, 900)
        self.setMinimumSize(900, 600)

        self._settings = settings or AppSettings()
        self._store = LocalStore(LOCAL_METADATA_PATH)

        # QtAds: configure before creating the dock manager.
        ads.CDockManager.setConfigFlags(
            ads.CDockManager.DefaultOpaqueConfig
        )
        ads.CDockManager.setConfigFlag(ads.CDockManager.DockAreaHasTabsMenuButton, False)
        ads.CDockManager.setConfigFlag(ads.CDockManager.DockAreaHasUndockButton, False)
        ads.CDockManager.setConfigFlag(ads.CDockManager.AlwaysShowTabs, True)
        ads.CDockManager.setConfigFlag(ads.CDockManager.EqualSplitOnInsertion, True)
        ads.CDockManager.setConfigFlag(ads.CDockManager.OpaqueSplitterResize, True)
        ads.CDockManager.setConfigFlag(ads.CDockManager.FocusHighlighting, False)
        ads.CDockManager.setConfigFlag(ads.CDockManager.DockAreaHasCloseButton, False)

        self._dock_manager = ads.CDockManager(self)
        self.setCentralWidget(self._dock_manager)

        self._icon_cache: dict[str, QIcon] = {}

        self._build_toolbar()
        self._build_status_bar()
        self._build_panels()
        self._restore_layout()

        # Auto-save layout periodically (every 30 s) and on dock changes.
        self._layout_timer = QTimer(self)
        self._layout_timer.setInterval(30_000)
        self._layout_timer.timeout.connect(self._save_layout)
        self._layout_timer.start()
        self._dock_manager.dockAreasAdded.connect(self._save_layout)
        self._dock_manager.dockAreasRemoved.connect(self._save_layout)

    # ------------------------------------------------------------------
    # Toolbar
    # ------------------------------------------------------------------

    def _build_toolbar(self) -> None:
        """Build the top toolbar."""
        toolbar = QToolBar("Main")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(18, 18))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        toolbar.addAction("About", self._on_about)
        toolbar.addSeparator()

        # Panels menu — lets user toggle panel visibility.
        self._panels_menu = QMenu(self)
        panels_action = toolbar.addAction("Panels")
        panels_action.setToolTip("Toggle panel visibility")
        # Attach the menu to the tool button so it opens on click.
        panels_btn = toolbar.widgetForAction(panels_action)
        if isinstance(panels_btn, QToolButton):
            panels_btn.setMenu(self._panels_menu)
            panels_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        toolbar.addSeparator()

        # Settings
        toolbar.addAction("Settings", self._on_settings)

        toolbar.addSeparator()

        # Reset layout
        toolbar.addAction("Reset Layout", self._reset_layout)

        self.addToolBar(toolbar)

    def _build_status_bar(self) -> None:
        """Build the status bar."""
        sb = QStatusBar()
        sb.showMessage("Ready")
        self.setStatusBar(sb)

    # ------------------------------------------------------------------
    # Icon helper
    # ------------------------------------------------------------------

    def _icon_for(self, name: str) -> QIcon:
        """Return the cached QIcon for a panel / tab name.

        Args:
            name: The display name used in ``TAB_ICONS``.

        Returns:
            A QIcon loaded from the matching SVG, or an empty QIcon if
            no mapping exists.
        """
        if name in self._icon_cache:
            return self._icon_cache[name]

        filename = TAB_ICONS.get(name, "")
        icon = QIcon()
        if filename:
            path = os.path.join(ICONS_DIR, filename)
            if os.path.isfile(path):
                icon = QIcon(path)
        self._icon_cache[name] = icon
        return icon

    @staticmethod
    def _hide_tab_label(dock: ads.CDockWidget) -> None:
        """Hide the text label inside a dock widget’s tab, leaving only the icon.

        Finds the internal QLabel child of the CDockWidgetTab and collapses
        it so only the SVG icon is visible. Sets a fixed tab size to ensure
        the icon renders at full resolution. The full panel name remains
        accessible via the tab's tooltip.

        Args:
            dock: The dock widget whose tab text should be hidden.
        """
        tab = dock.tabWidget()
        if tab is None:
            return
        tab.setToolTip(dock.windowTitle())
        tab.setIconSize(QSize(32, 32))
        tab.setFixedHeight(48)
        tab.setMinimumWidth(52)
        # Hide only the CElidingLabel (text), keep the QLabel (icon) visible.
        for child in tab.children():
            class_name = type(child).__name__
            if class_name == "CElidingLabel":
                child.setMaximumWidth(0)
                child.setVisible(False)

    # ------------------------------------------------------------------
    # Panel construction
    # ------------------------------------------------------------------

    def _build_panels(self) -> None:
        """Create all dockable panels and arrange them."""
        # --- Brushes panel (main content) ---
        brushes_widget = self._build_brushes_panel()
        brushes_dock = ads.CDockWidget("Brushes")
        brushes_dock.setWidget(brushes_widget)
        brushes_dock.setIcon(self._icon_for("Brushes"))
        brushes_dock.setFeature(ads.CDockWidget.DockWidgetClosable, False)
        brushes_dock.setMinimumSizeHintMode(
            ads.CDockWidget.MinimumSizeHintFromContent
        )
        center_area = self._dock_manager.addDockWidget(
            ads.DockWidgetArea.CenterDockWidgetArea, brushes_dock
        )
        self._hide_tab_label(brushes_dock)

        # --- Metadata panel (right side) ---
        metadata_widget = self._build_metadata_panel()
        metadata_dock = ads.CDockWidget("Metadata")
        metadata_dock.setWidget(metadata_widget)
        metadata_dock.setIcon(self._icon_for("Metadata"))
        metadata_dock.setFeature(ads.CDockWidget.DockWidgetClosable, False)
        metadata_dock.setMinimumWidth(320)
        self._dock_manager.addDockWidget(
            ads.DockWidgetArea.RightDockWidgetArea, metadata_dock
        )

        # --- Favorites panel (left side, collapsible) ---
        favorites_widget = self._build_favorites_panel()
        favorites_dock = ads.CDockWidget("Favorites")
        favorites_dock.setWidget(favorites_widget)
        favorites_dock.setIcon(self._icon_for("Favorites"))
        favorites_dock.setFeature(ads.CDockWidget.DockWidgetClosable, False)
        favorites_dock.setMinimumWidth(200)
        self._dock_manager.addDockWidget(
            ads.DockWidgetArea.LeftDockWidgetArea, favorites_dock
        )

        # --- Placeholder panels for other asset types (tabbed behind Brushes) ---
        for tab_name in ASSET_TABS:
            if tab_name == "Brushes":
                continue
            placeholder = self._build_placeholder_panel(tab_name)
            dock = ads.CDockWidget(tab_name)
            dock.setWidget(placeholder)
            dock.setIcon(self._icon_for(tab_name))
            dock.setFeature(ads.CDockWidget.DockWidgetClosable, False)
            self._dock_manager.addDockWidget(
                ads.DockWidgetArea.CenterDockWidgetArea, dock, center_area
            )
            self._hide_tab_label(dock)

        # Activate Brushes as the first visible center tab.
        center_area.setCurrentIndex(0)

        # Populate the Panels toggle menu with one entry per dock widget.
        self._populate_panels_menu()

    # ------------------------------------------------------------------
    # Panels visibility menu
    # ------------------------------------------------------------------

    def _populate_panels_menu(self) -> None:
        """Fill the Panels toolbar menu with a toggle action per dock widget."""
        self._panels_menu.clear()
        for dock in self._dock_manager.dockWidgetsMap().values():
            action = dock.toggleViewAction()
            action.setIcon(self._icon_for(dock.windowTitle()))
            self._panels_menu.addAction(action)

    # ------------------------------------------------------------------
    # Layout persistence
    # ------------------------------------------------------------------

    def _save_layout(self) -> None:
        """Save the current dock layout to disk (called automatically)."""
        state = self._dock_manager.saveState()
        os.makedirs(os.path.dirname(LAYOUT_STATE_PATH), exist_ok=True)
        with open(LAYOUT_STATE_PATH, "wb") as f:
            f.write(state.data())

    def _restore_layout(self) -> None:
        """Restore a previously saved dock layout from disk, if it exists."""
        if not os.path.isfile(LAYOUT_STATE_PATH):
            return
        try:
            with open(LAYOUT_STATE_PATH, "rb") as f:
                data = f.read()
            state = QByteArray(data)
            self._dock_manager.restoreState(state)
            self.statusBar().showMessage("Layout restored", 3000)
        except Exception:
            # If the file is corrupt or incompatible, just ignore it.
            pass

    def _reset_layout(self) -> None:
        """Delete the saved layout and restart with default arrangement."""
        if os.path.isfile(LAYOUT_STATE_PATH):
            os.remove(LAYOUT_STATE_PATH)
        self.statusBar().showMessage(
            "Layout reset — restart the app to apply", 5000
        )

    def closeEvent(self, event) -> None:
        """Auto-save the layout when the window is closed.

        Args:
            event: The close event.
        """
        self._save_layout()
        super().closeEvent(event)

    # ------------------------------------------------------------------
    # Brushes panel
    # ------------------------------------------------------------------

    def _build_brushes_panel(self) -> QWidget:
        """Build the grid-based Brushes browser panel.

        Returns:
            The constructed QWidget.
        """
        self._brush_grid = BrushGridWidget()
        self._brush_grid.brush_selected.connect(self._on_brush_selected)
        self._scan_brushes()
        return self._brush_grid

    # ------------------------------------------------------------------
    # Metadata panel
    # ------------------------------------------------------------------

    def _build_metadata_panel(self) -> QWidget:
        """Build the metadata editing panel.

        Returns:
            The constructed QWidget.
        """
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self._info_label = QLabel("Select a brush")
        self._info_label.setProperty("heading", True)
        layout.addWidget(self._info_label)

        # Form
        form_group = QGroupBox("Details")
        form = QFormLayout(form_group)
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._desc_edit = QTextEdit()
        self._desc_edit.setMaximumHeight(80)
        self._desc_edit.setPlaceholderText("Enter description…")
        form.addRow("Description", self._desc_edit)

        self._type_combo = QComboBox()
        self._type_combo.addItem("")
        self._type_combo.addItems(BRUSH_TYPES)
        form.addRow("Type", self._type_combo)

        self._category_edit = QLineEdit()
        self._category_edit.setPlaceholderText("Enter category…")
        form.addRow("Category", self._category_edit)

        self._tags_edit = QLineEdit()
        self._tags_edit.setPlaceholderText("Comma-separated tags…")
        form.addRow("Tags", self._tags_edit)

        self._author_edit = QLineEdit()
        self._author_edit.setPlaceholderText("Enter author / credit…")
        form.addRow("Author", self._author_edit)

        self._fav_btn = QPushButton("☆  Mark as Favorite")
        self._fav_btn.setCheckable(True)
        form.addRow("Favorite", self._fav_btn)

        layout.addWidget(form_group)

        # Save button (accent style)
        save_btn = QPushButton("Save Metadata")
        save_btn.setProperty("accent", True)
        save_btn.clicked.connect(self._on_save_metadata)
        layout.addWidget(save_btn)

        layout.addStretch()
        return container

    # ------------------------------------------------------------------
    # Favorites panel
    # ------------------------------------------------------------------

    def _build_favorites_panel(self) -> QWidget:
        """Build the favorites list panel.

        Returns:
            The constructed QWidget.
        """
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QLabel("Favorites")
        header.setProperty("heading", True)
        layout.addWidget(header)

        self._fav_list = QListWidget()
        self._fav_list.setAlternatingRowColors(True)
        self._fav_list.itemDoubleClicked.connect(self._on_fav_double_clicked)
        layout.addWidget(self._fav_list)

        self._refresh_favorites_list()
        return container

    # ------------------------------------------------------------------
    # Placeholder panel
    # ------------------------------------------------------------------

    def _build_placeholder_panel(self, name: str) -> QWidget:
        """Build a placeholder panel for a not-yet-implemented asset type.

        Args:
            name: The display name for the panel.

        Returns:
            A QWidget with a placeholder message.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel(f"{name}\nComing soon")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setProperty("secondary", True)
        label.setStyleSheet("font-size: 18px;")
        layout.addWidget(label)
        return widget

    # ------------------------------------------------------------------
    # Brush list helpers
    # ------------------------------------------------------------------

    def _scan_brushes(self) -> None:
        """Scan for brushes using the configured ZBrush path."""
        zbrush_path = self._settings.zbrush_path
        if not zbrush_path:
            return

        brushes = scan_brush_directories(
            zbrush_path,
            on_progress=lambda cur, tot, name: self.statusBar().showMessage(
                f"Scanning brushes… {cur}/{tot}: {name}"
            ),
        )
        self._brush_grid.set_brushes(brushes)
        self._brush_grid.set_favorites(set(self._store.get_favorites()))
        self.statusBar().showMessage(f"Found {len(brushes)} brushes", 5000)

    def _refresh_favorites_list(self) -> None:
        """Reload the favorites panel list."""
        self._fav_list.clear()
        for name in self._store.get_favorites():
            item = QListWidgetItem(f"★  {name}")
            item.setData(Qt.ItemDataRole.UserRole, name)
            self._fav_list.addItem(item)

    def _load_metadata_into_panel(self, meta: BrushMetadata) -> None:
        """Populate the metadata form fields from a BrushMetadata instance.

        Args:
            meta: The metadata to display.
        """
        self._info_label.setText(meta.name or "Select a brush")
        self._desc_edit.setPlainText(meta.description)

        idx = self._type_combo.findText(meta.brush_type)
        self._type_combo.setCurrentIndex(max(idx, 0))

        self._category_edit.setText(meta.category)
        self._tags_edit.setText(", ".join(meta.tags))
        self._author_edit.setText(meta.author)
        self._fav_btn.setChecked(meta.favorite)
        self._fav_btn.setText(
            "★  Favorite" if meta.favorite else "☆  Mark as Favorite"
        )

    def _current_brush_name(self) -> str | None:
        """Return the brush name from the currently selected grid item.

        Returns:
            The brush name, or None if nothing is selected.
        """
        return self._brush_grid.current_brush_name()

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    @Slot()
    def _on_about(self) -> None:
        """Show the About dialog."""
        QMessageBox.about(
            self,
            "About",
            f"{APP_NAME}  {APP_VERSION}\n\nAsset organizer for ZBrush.",
        )

    @Slot()
    def _on_settings(self) -> None:
        """Open the Settings dialog."""
        dlg = SettingsDialog(self._settings, parent=self)
        dlg.exec()

    @Slot(str, str)
    def _on_brush_selected(self, name: str, path: str) -> None:
        """Handle brush selection change in the grid.

        Args:
            name: The selected brush name.
            path: The selected brush file path.
        """
        if not name:
            return
        meta = self._store.get_brush(name)
        meta.file_path = path
        self._load_metadata_into_panel(meta)

    @Slot()
    def _on_save_metadata(self) -> None:
        """Save the current metadata form back to the store."""
        name = self._brush_grid.current_brush_name()
        if name is None:
            return

        meta = self._store.get_brush(name)
        meta.description = self._desc_edit.toPlainText().strip()
        meta.brush_type = self._type_combo.currentText()
        meta.category = self._category_edit.text().strip()
        meta.tags = [
            t.strip() for t in self._tags_edit.text().split(",") if t.strip()
        ]
        meta.author = self._author_edit.text().strip()
        meta.favorite = self._fav_btn.isChecked()
        self._store.put_brush(meta)

        # Refresh favorites.
        self._brush_grid.set_favorites(set(self._store.get_favorites()))
        self._refresh_favorites_list()

        self.statusBar().showMessage(f"Saved metadata for '{name}'", 3000)

    @Slot(QListWidgetItem)
    def _on_fav_double_clicked(self, item: QListWidgetItem) -> None:
        """Jump to a brush when double-clicked in the favorites panel.

        Args:
            item: The clicked list item.
        """
        name = item.data(Qt.ItemDataRole.UserRole)
        if name is None:
            return
        meta = self._store.get_brush(name)
        self._load_metadata_into_panel(meta)
