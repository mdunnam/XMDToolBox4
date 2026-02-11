"""Auto-detect ZBrush installations on Windows.

Scans the Windows registry and common ``Program Files`` directories
for Maxon ZBrush installs. Returns a list of ``(version, path)`` tuples
sorted newest-first.
"""

from __future__ import annotations

import os
import re
from typing import NamedTuple

try:
    import winreg  # Windows only
except ImportError:
    winreg = None  # type: ignore[assignment]


class ZBrushInstall(NamedTuple):
    """A detected ZBrush installation."""

    version: str
    path: str


def detect_zbrush_installs() -> list[ZBrushInstall]:
    """Return all detected ZBrush installations, newest first.

    Detection strategy (Windows):
        1. Scan ``HKLM\\SOFTWARE\\Maxon`` registry keys for install paths.
        2. Scan ``Program Files`` and ``Program Files (x86)`` for
           directories matching ``Maxon ZBrush*``.
        3. De-duplicate by resolved path and sort by version descending.

    Returns:
        A list of :class:`ZBrushInstall` tuples.
    """
    found: dict[str, ZBrushInstall] = {}

    # --- Registry scan ---
    if winreg is not None:
        _scan_registry(found)

    # --- Filesystem scan ---
    _scan_program_files(found)

    # Sort newest version first.
    installs = list(found.values())
    installs.sort(key=lambda i: _version_key(i.version), reverse=True)
    return installs


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------

_VERSION_RE = re.compile(r"(\d[\d.]*)")


def _extract_version(text: str) -> str:
    """Pull a version string like '2026.1.1' out of *text*.

    Args:
        text: A string that may contain a version number.

    Returns:
        The extracted version or ``'0'`` if none found.
    """
    m = _VERSION_RE.search(text)
    return m.group(1) if m else "0"


def _version_key(version: str) -> tuple[int, ...]:
    """Convert a dotted version string into a sortable tuple.

    Args:
        version: A version string like ``'2026.1.1'``.

    Returns:
        A tuple of ints for comparison.
    """
    parts: list[int] = []
    for segment in version.split("."):
        try:
            parts.append(int(segment))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def _looks_like_zbrush(path: str) -> bool:
    """Heuristic: does *path* contain a ZBrush executable?

    Args:
        path: A directory path.

    Returns:
        True if a ZBrush executable is found.
    """
    if not os.path.isdir(path):
        return False
    for name in ("ZBrush.exe", "ZBrushCore.exe"):
        if os.path.isfile(os.path.join(path, name)):
            return True
    # Also accept if typical ZBrush folders exist.
    return os.path.isdir(os.path.join(path, "ZStartup"))


def _add_install(found: dict[str, ZBrushInstall], path: str) -> None:
    """Add *path* to *found* if it looks like a valid ZBrush install.

    Args:
        found: The accumulator dict keyed by normalised path.
        path: Candidate directory.
    """
    path = os.path.normpath(path)
    if path in found:
        return
    if not _looks_like_zbrush(path):
        return
    version = _extract_version(os.path.basename(path))
    found[path] = ZBrushInstall(version=version, path=path)


def _scan_registry(found: dict[str, ZBrushInstall]) -> None:
    """Scan the Windows registry for ZBrush install paths.

    Args:
        found: The accumulator dict.
    """
    if winreg is None:
        return

    # Maxon registers under several possible keys.
    roots = [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]
    sub_keys = [
        r"SOFTWARE\Maxon",
        r"SOFTWARE\Pixologic",
        r"SOFTWARE\WOW6432Node\Maxon",
        r"SOFTWARE\WOW6432Node\Pixologic",
    ]
    for root in roots:
        for sub in sub_keys:
            try:
                key = winreg.OpenKey(root, sub)
            except OSError:
                continue
            try:
                i = 0
                while True:
                    try:
                        child_name = winreg.EnumKey(key, i)
                        child = winreg.OpenKey(key, child_name)
                        try:
                            val, _ = winreg.QueryValueEx(child, "InstallPath")
                            if isinstance(val, str) and val:
                                _add_install(found, val)
                        except OSError:
                            pass
                        finally:
                            winreg.CloseKey(child)
                    except OSError:
                        break
                    i += 1
            finally:
                winreg.CloseKey(key)


def _scan_program_files(found: dict[str, ZBrushInstall]) -> None:
    """Scan Program Files directories for ZBrush folders.

    Args:
        found: The accumulator dict.
    """
    program_dirs: list[str] = []
    for env_var in ("ProgramFiles", "ProgramFiles(x86)", "ProgramW6432"):
        val = os.environ.get(env_var)
        if val and os.path.isdir(val):
            program_dirs.append(val)

    for pdir in program_dirs:
        try:
            entries = os.listdir(pdir)
        except OSError:
            continue
        for entry in entries:
            lower = entry.lower()
            if "zbrush" in lower or "maxon" in lower:
                candidate = os.path.join(pdir, entry)
                if os.path.isdir(candidate):
                    _add_install(found, candidate)
                    # Also check sub-folders (e.g. "Maxon/ZBrush 2026")
                    try:
                        for sub in os.listdir(candidate):
                            sub_path = os.path.join(candidate, sub)
                            if os.path.isdir(sub_path) and "zbrush" in sub.lower():
                                _add_install(found, sub_path)
                    except OSError:
                        pass
