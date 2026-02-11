"""UI construction for XMD ToolBox."""

from __future__ import annotations

from zbrush import commands as zbc

from . import commands
from .config import ASSET_TABS, DEFAULT_ASSET_TAB, SUBPALETTE_MAIN


def build_palette(palette_name: str) -> None:
    """Create or rebuild the main plugin palette.

    Args:
        palette_name: The top-level palette label.
    """
    if zbc.exists(palette_name):
        zbc.close(palette_name)

    zbc.add_palette(palette_name, docking_bar=1)
    subpalette_path = f"{palette_name}:{SUBPALETTE_MAIN}"
    zbc.add_subpalette(subpalette_path, title_mode=2)

    button_path = f"{subpalette_path}:About"
    zbc.add_button(button_path, "Show plugin info", commands.show_about, width=1.0)

    tabs_path = f"{palette_name}:Tabs"
    zbc.add_subpalette(tabs_path, title_mode=2)
    for tab_name in ASSET_TABS:
        switch_path = f"{tabs_path}:{tab_name}"
        is_default = tab_name == DEFAULT_ASSET_TAB
        zbc.add_switch(switch_path, is_default, "Asset tab", _on_tab_changed, width=1.0)

    for tab_name in ASSET_TABS:
        content_path = f"{palette_name}:{tab_name}"
        zbc.add_subpalette(content_path, title_mode=2)
        if tab_name == "Brushes":
            _build_brushes_tab(content_path)
        else:
            # Placeholder content for future asset types.
            zbc.add_button(
                f"{content_path}:Coming Soon",
                "Placeholder. Asset UI not implemented yet.",
                None,
                initially_disabled=True,
                width=1.0,
            )

    _select_tab(palette_name, DEFAULT_ASSET_TAB)


def _on_tab_changed(sender: str, value: bool) -> None:
    """Switch asset tabs when a tab switch is toggled on.

    Args:
        sender: The item path of the tab switch.
        value: The current switch state.
    """
    if not value:
        return

    palette_name = sender.split(":Tabs", 1)[0]
    tab_name = sender.rsplit(":", 1)[-1]
    _select_tab(palette_name, tab_name)


def _select_tab(palette_name: str, tab_name: str) -> None:
    """Show the selected tab and hide the others.

    Args:
        palette_name: The top-level palette name.
        tab_name: The selected tab label.
    """
    tabs_path = f"{palette_name}:Tabs"
    for name in ASSET_TABS:
        content_path = f"{palette_name}:{name}"
        if name == tab_name:
            zbc.show(content_path)
        else:
            zbc.hide(content_path)

    for name in ASSET_TABS:
        switch_path = f"{tabs_path}:{name}"
        zbc.set(switch_path, name == tab_name)


def _build_brushes_tab(content_path: str) -> None:
    """Build the Brushes tab UI controls.

    Args:
        content_path: The item path of the Brushes sub-palette.
    """
    # --- Metadata editing section ---
    meta_path = f"{content_path}:Metadata"
    zbc.add_subpalette(meta_path, title_mode=0)

    zbc.add_button(
        f"{meta_path}:Show Info",
        "Show all metadata for the active brush.",
        commands.show_brush_info,
        width=1.0,
    )
    zbc.add_button(
        f"{meta_path}:Description",
        "Set description for the active brush.",
        commands.set_brush_description,
        width=1.0,
    )
    zbc.add_button(
        f"{meta_path}:Type",
        "Set brush type for the active brush.",
        commands.set_brush_type,
        width=1.0,
    )
    zbc.add_button(
        f"{meta_path}:Category",
        "Set category for the active brush.",
        commands.set_brush_category,
        width=1.0,
    )
    zbc.add_button(
        f"{meta_path}:Tags",
        "Set tags for the active brush (comma-separated).",
        commands.set_brush_tags,
        width=1.0,
    )
    zbc.add_button(
        f"{meta_path}:Author",
        "Set author/credit for the active brush.",
        commands.set_brush_author,
        width=1.0,
    )
    zbc.add_switch(
        f"{meta_path}:Favorite",
        False,
        "Toggle favorite for the active brush.",
        commands.toggle_brush_favorite,
        width=1.0,
    )

    # --- Search and Favorites section ---
    find_path = f"{content_path}:Find"
    zbc.add_subpalette(find_path, title_mode=0)

    zbc.add_button(
        f"{find_path}:Search",
        "Search brushes by name, tags, type, or category.",
        commands.search_brushes,
        width=1.0,
    )
    zbc.add_button(
        f"{find_path}:Favorites",
        "Show all brushes marked as favorites.",
        commands.show_favorites,
        width=1.0,
    )
