"""Launcher script for XMD ToolBox.

Load this file in ZBrush via ZScript > Python Scripting > Load to start the plugin.
"""

import os
import sys

# Add the parent directory of xmd_toolbox to sys.path so the package can be imported.
_plugin_root: str = os.path.dirname(os.path.abspath(__file__))
if _plugin_root not in sys.path:
    sys.path.insert(0, _plugin_root)

from xmd_toolbox import initialize

initialize()

# Clean up sys.path to avoid polluting the shared interpreter.
if _plugin_root in sys.path:
    sys.path.remove(_plugin_root)
