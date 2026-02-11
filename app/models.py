"""Brush metadata data model for XMD ToolBox."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class BrushMetadata:
    """Metadata for a single ZBrush brush.

    Attributes:
        name: The brush name as shown in ZBrush. This is the primary identifier.
        description: A free-text description of the brush.
        brush_type: The brush type label (e.g. "Standard", "Clay", "Insert MultiMesh").
        category: A user-defined category string.
        tags: A list of user-defined tag strings.
        author: The author or credit string.
        favorite: Whether the brush is marked as a favorite.
        file_path: The absolute path to the brush file on disk.
        scan_date: ISO timestamp of when the brush was last scanned.
    """

    name: str = ""
    description: str = ""
    brush_type: str = ""
    category: str = ""
    tags: list[str] = field(default_factory=list)
    author: str = ""
    favorite: bool = False
    file_path: str = ""
    scan_date: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize this metadata to a plain dict.

        Returns:
            A dict suitable for JSON serialization.
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BrushMetadata:
        """Deserialize metadata from a plain dict.

        Args:
            data: A dict as produced by ``to_dict``.

        Returns:
            A new BrushMetadata instance.
        """
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            brush_type=data.get("brush_type", ""),
            category=data.get("category", ""),
            tags=list(data.get("tags", [])),
            author=data.get("author", ""),
            favorite=bool(data.get("favorite", False)),
            file_path=data.get("file_path", ""),
            scan_date=data.get("scan_date", ""),
        )
