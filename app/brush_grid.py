"""Grid-based brush browser widget.

Displays scanned brushes as a grid of thumbnail icons with labels.
Supports search filtering, favorites toggle, and selection.
"""

from __future__ import annotations

import os
from typing import Optional

from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QImage, QPixmap, QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .brush_scanner import ScannedBrush
from .zbp_thumbnail import ICON_WIDTH, ICON_HEIGHT


# Grid icon display size.
_THUMB_SIZE = 72
_GRID_SPACING = 4


class BrushGridWidget(QWidget):
    """Thumbnail grid for browsing brushes.

    Emits :pyqtSignal:`brush_selected` when the user clicks a brush.
    """

    brush_selected = Signal(str, str)  # (name, path)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._brushes: list[ScannedBrush] = []
        self._visible: list[ScannedBrush] = []
        self._favorites: set[str] = set()
        self._show_favorites_only: bool = False
        self._filter_text: str = ""
        self._pixmap_cache: dict[str, QPixmap] = {}

        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Build the widget layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Search row
        search_row = QHBoxLayout()
        search_row.setSpacing(8)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search brushes…")
        self._search_input.setClearButtonEnabled(True)
        self._search_input.textChanged.connect(self._on_search_changed)
        search_row.addWidget(self._search_input)

        self._favorites_btn = QPushButton("★ Favorites")
        self._favorites_btn.setCheckable(True)
        self._favorites_btn.setFixedWidth(110)
        self._favorites_btn.toggled.connect(self._on_favorites_toggled)
        search_row.addWidget(self._favorites_btn)

        layout.addLayout(search_row)

        # Count label
        self._count_label = QLabel("")
        self._count_label.setProperty("secondary", True)
        layout.addWidget(self._count_label)

        # Grid (QListWidget in icon mode)
        self._grid = QListWidget()
        self._grid.setViewMode(QListView.ViewMode.IconMode)
        self._grid.setIconSize(QSize(_THUMB_SIZE, _THUMB_SIZE))
        self._grid.setGridSize(QSize(_THUMB_SIZE + 24, _THUMB_SIZE + 32))
        self._grid.setSpacing(_GRID_SPACING)
        self._grid.setResizeMode(QListView.ResizeMode.Adjust)
        self._grid.setWrapping(True)
        self._grid.setWordWrap(True)
        self._grid.setUniformItemSizes(True)
        self._grid.setMovement(QListView.Movement.Static)
        self._grid.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self._grid.setTextElideMode(Qt.TextElideMode.ElideRight)
        self._grid.currentItemChanged.connect(self._on_item_changed)
        layout.addWidget(self._grid)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_brushes(self, brushes: list[ScannedBrush]) -> None:
        """Load a list of scanned brushes into the grid.

        Args:
            brushes: The brushes to display.
        """
        self._brushes = brushes
        self._apply_filter()

    def set_favorites(self, favorites: set[str]) -> None:
        """Set the current favorites set for filtering.

        Args:
            favorites: Set of brush names marked as favorites.
        """
        self._favorites = favorites
        if self._show_favorites_only:
            self._apply_filter()

    def current_brush_name(self) -> Optional[str]:
        """Return the name of the currently selected brush.

        Returns:
            Brush name or None.
        """
        item = self._grid.currentItem()
        if item is None:
            return None
        return item.data(Qt.ItemDataRole.UserRole)

    def current_brush_path(self) -> Optional[str]:
        """Return the file path of the currently selected brush.

        Returns:
            Brush path or None.
        """
        item = self._grid.currentItem()
        if item is None:
            return None
        return item.data(Qt.ItemDataRole.UserRole + 1)

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def _apply_filter(self) -> None:
        """Rebuild the grid based on current filter and favorites state."""
        query = self._filter_text.lower()
        visible = self._brushes

        if query:
            visible = [b for b in visible if query in b.name.lower()]

        if self._show_favorites_only:
            visible = [b for b in visible if b.name in self._favorites]

        self._visible = visible
        self._rebuild_grid()

    def _rebuild_grid(self) -> None:
        """Populate the QListWidget with thumbnail items."""
        self._grid.clear()
        self._count_label.setText(f"{len(self._visible)} brushes")

        for brush in self._visible:
            pixmap = self._get_pixmap(brush)

            # When no thumbnail, create a dark placeholder so the label
            # stays at the same vertical position as icons with thumbnails.
            if pixmap:
                icon = QIcon(pixmap)
            else:
                placeholder = QPixmap(_THUMB_SIZE, _THUMB_SIZE)
                placeholder.fill(Qt.GlobalColor.transparent)
                icon = QIcon(placeholder)

            item = QListWidgetItem(icon, brush.name)
            item.setData(Qt.ItemDataRole.UserRole, brush.name)
            item.setData(Qt.ItemDataRole.UserRole + 1, brush.path)
            item.setToolTip(f"{brush.name}\n{brush.category}\n{brush.path}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
            item.setSizeHint(QSize(_THUMB_SIZE + 24, _THUMB_SIZE + 32))
            self._grid.addItem(item)

    # ------------------------------------------------------------------
    # Thumbnail loading
    # ------------------------------------------------------------------

    def _get_pixmap(self, brush: ScannedBrush) -> Optional[QPixmap]:
        """Load or retrieve a cached pixmap for a brush icon.

        Args:
            brush: The brush to load the icon for.

        Returns:
            A QPixmap or None if no thumbnail is available.
        """
        if brush.thumb_path in self._pixmap_cache:
            return self._pixmap_cache[brush.thumb_path]

        if not brush.thumb_path or not os.path.isfile(brush.thumb_path):
            return None

        try:
            with open(brush.thumb_path, "rb") as f:
                raw = f.read()

            if len(raw) < ICON_WIDTH * ICON_HEIGHT * 4:
                return None

            image = QImage(
                raw,
                ICON_WIDTH,
                ICON_HEIGHT,
                ICON_WIDTH * 4,
                QImage.Format.Format_RGBA8888,
            )
            # QImage from raw bytes needs to keep the data alive,
            # so we copy it immediately.
            image = image.copy()
            pixmap = QPixmap.fromImage(image)

            # Scale up for the grid display.
            if pixmap.width() != _THUMB_SIZE:
                pixmap = pixmap.scaled(
                    _THUMB_SIZE,
                    _THUMB_SIZE,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )

            self._pixmap_cache[brush.thumb_path] = pixmap
            return pixmap

        except OSError:
            return None

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    @Slot(str)
    def _on_search_changed(self, text: str) -> None:
        """Handle search text changes.

        Args:
            text: The current search text.
        """
        self._filter_text = text
        self._apply_filter()

    @Slot(bool)
    def _on_favorites_toggled(self, checked: bool) -> None:
        """Toggle favorites-only filtering.

        Args:
            checked: Whether favorites filter is active.
        """
        self._show_favorites_only = checked
        self._apply_filter()

    @Slot()
    def _on_item_changed(self) -> None:
        """Emit brush_selected when the user clicks a brush."""
        name = self.current_brush_name()
        path = self.current_brush_path()
        if name:
            self.brush_selected.emit(name, path or "")
