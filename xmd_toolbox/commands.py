"""Command callbacks for XMD ToolBox.

Commands are wired to UI elements in ui.py. Each callback receives the
sender item path and optionally a value from switches/sliders.
"""

from __future__ import annotations

from zbrush import commands as zbc

from .config import BRUSH_TYPES, LOCAL_METADATA_PATH
from .local_store import LocalStore
from .models import BrushMetadata

# ---------------------------------------------------------------------------
# Module-level store instance.
# Created on first access so the file is only touched when needed.
# ---------------------------------------------------------------------------
_store: LocalStore | None = None


def _get_store() -> LocalStore:
    """Return the singleton LocalStore instance.

    Returns:
        The active LocalStore.
    """
    global _store
    if _store is None:
        _store = LocalStore(LOCAL_METADATA_PATH)
    return _store


def _get_active_brush_name() -> str | None:
    """Return the name of the currently active brush in ZBrush.

    Uses the item path ``Brush`` to read the active brush label.

    Returns:
        The brush name string, or None if it cannot be determined.
    """
    try:
        title: str = zbc.get_title("Brush")
        if title:
            return title.strip()
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# General
# ---------------------------------------------------------------------------

def show_about(sender: str) -> None:
    """Show a basic About dialog for the plugin.

    Args:
        sender: The item path of the button that invoked the callback.
    """
    zbc.message_ok("XMD ToolBox v4.0\nZBrush 2026.1\n\nAsset organizer for ZBrush.", "About")


# ---------------------------------------------------------------------------
# Brush metadata — Description
# ---------------------------------------------------------------------------

def set_brush_description(sender: str) -> None:
    """Prompt the user to set or edit the description of the active brush.

    Args:
        sender: The item path of the button that invoked the callback.
    """
    brush_name = _get_active_brush_name()
    if not brush_name:
        zbc.message_ok("No active brush detected.", "XMD ToolBox")
        return

    store = _get_store()
    meta = store.get_brush(brush_name)

    new_desc = zbc.ask_string(f"Description for '{brush_name}':", meta.description)
    if new_desc is None:
        return  # User cancelled.

    meta.description = new_desc
    store.put_brush(meta)


# ---------------------------------------------------------------------------
# Brush metadata — Type (dropdown via note buttons)
# ---------------------------------------------------------------------------

def set_brush_type(sender: str) -> None:
    """Show a type picker for the active brush.

    Uses note buttons to simulate a dropdown since the ZBrush API does not
    provide a native dropdown widget.

    Args:
        sender: The item path of the button that invoked the callback.
    """
    brush_name = _get_active_brush_name()
    if not brush_name:
        zbc.message_ok("No active brush detected.", "XMD ToolBox")
        return

    store = _get_store()
    meta = store.get_brush(brush_name)

    # Build a note with one button per brush type.
    for i, bt in enumerate(BRUSH_TYPES):
        is_current = bt == meta.brush_type
        zbc.add_note_button(
            bt, "", is_current, False,
            10, 10 + i * 20, 200, 18,
        )

    action = zbc.show_note(f"Select type for '{brush_name}':")
    # action is the 1-based index of the pressed button.
    if 1 <= action <= len(BRUSH_TYPES):
        meta.brush_type = BRUSH_TYPES[action - 1]
        store.put_brush(meta)


# ---------------------------------------------------------------------------
# Brush metadata — Category
# ---------------------------------------------------------------------------

def set_brush_category(sender: str) -> None:
    """Prompt the user to set or edit the category of the active brush.

    Args:
        sender: The item path of the button that invoked the callback.
    """
    brush_name = _get_active_brush_name()
    if not brush_name:
        zbc.message_ok("No active brush detected.", "XMD ToolBox")
        return

    store = _get_store()
    meta = store.get_brush(brush_name)

    new_cat = zbc.ask_string(f"Category for '{brush_name}':", meta.category)
    if new_cat is None:
        return

    meta.category = new_cat
    store.put_brush(meta)


# ---------------------------------------------------------------------------
# Brush metadata — Tags
# ---------------------------------------------------------------------------

def set_brush_tags(sender: str) -> None:
    """Prompt the user to set or edit tags for the active brush.

    Tags are entered as a comma-separated string.

    Args:
        sender: The item path of the button that invoked the callback.
    """
    brush_name = _get_active_brush_name()
    if not brush_name:
        zbc.message_ok("No active brush detected.", "XMD ToolBox")
        return

    store = _get_store()
    meta = store.get_brush(brush_name)

    current_tags = ", ".join(meta.tags)
    new_tags_str = zbc.ask_string(f"Tags for '{brush_name}' (comma-separated):", current_tags)
    if new_tags_str is None:
        return

    meta.tags = [t.strip() for t in new_tags_str.split(",") if t.strip()]
    store.put_brush(meta)


# ---------------------------------------------------------------------------
# Brush metadata — Author
# ---------------------------------------------------------------------------

def set_brush_author(sender: str) -> None:
    """Prompt the user to set or edit the author/credit for the active brush.

    Args:
        sender: The item path of the button that invoked the callback.
    """
    brush_name = _get_active_brush_name()
    if not brush_name:
        zbc.message_ok("No active brush detected.", "XMD ToolBox")
        return

    store = _get_store()
    meta = store.get_brush(brush_name)

    new_author = zbc.ask_string(f"Author for '{brush_name}':", meta.author)
    if new_author is None:
        return

    meta.author = new_author
    store.put_brush(meta)


# ---------------------------------------------------------------------------
# Brush metadata — Favorite
# ---------------------------------------------------------------------------

def toggle_brush_favorite(sender: str, value: bool) -> None:
    """Toggle the favorite state for the active brush.

    Args:
        sender: The item path of the switch that invoked the callback.
        value: The current switch state.
    """
    brush_name = _get_active_brush_name()
    if not brush_name:
        zbc.message_ok("No active brush detected.", "XMD ToolBox")
        return

    store = _get_store()
    meta = store.get_brush(brush_name)
    meta.favorite = value
    store.put_brush(meta)


# ---------------------------------------------------------------------------
# Brush metadata — Show Info
# ---------------------------------------------------------------------------

def show_brush_info(sender: str) -> None:
    """Display stored metadata for the active brush.

    Args:
        sender: The item path of the button that invoked the callback.
    """
    brush_name = _get_active_brush_name()
    if not brush_name:
        zbc.message_ok("No active brush detected.", "XMD ToolBox")
        return

    store = _get_store()
    meta = store.get_brush(brush_name)

    tags_str = ", ".join(meta.tags) if meta.tags else "(none)"
    info = (
        f"Name: {meta.name}\n"
        f"Type: {meta.brush_type or '(not set)'}\n"
        f"Category: {meta.category or '(not set)'}\n"
        f"Tags: {tags_str}\n"
        f"Author: {meta.author or '(not set)'}\n"
        f"Favorite: {'Yes' if meta.favorite else 'No'}\n"
        f"Description: {meta.description or '(not set)'}"
    )
    zbc.message_ok(info, f"Brush Info — {brush_name}")


# ---------------------------------------------------------------------------
# Brush search
# ---------------------------------------------------------------------------

def search_brushes(sender: str) -> None:
    """Prompt for a search query and display matching brush names.

    Args:
        sender: The item path of the button that invoked the callback.
    """
    query = zbc.ask_string("Search brushes:", "")
    if not query:
        return

    store = _get_store()
    results = store.search(query)

    if results:
        msg = "\n".join(results[:50])  # Cap display at 50 results.
        if len(results) > 50:
            msg += f"\n... and {len(results) - 50} more."
        zbc.message_ok(msg, f"Search Results — '{query}'")
    else:
        zbc.message_ok(f"No brushes matching '{query}'.", "Search Results")


# ---------------------------------------------------------------------------
# Favorites list
# ---------------------------------------------------------------------------

def show_favorites(sender: str) -> None:
    """Display all brushes marked as favorites.

    Args:
        sender: The item path of the button that invoked the callback.
    """
    store = _get_store()
    favs = store.get_favorites()

    if favs:
        zbc.message_ok("\n".join(favs), "Favorite Brushes")
    else:
        zbc.message_ok("No favorite brushes set.", "Favorite Brushes")
