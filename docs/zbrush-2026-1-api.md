# ZBrush 2026.1 Python API Notes (Exhaustive, Factual)

This document is a strict, exhaustive reference for the ZBrush 2026.1 Python SDK. It only states facts from the official documentation and examples listed below.

## Sources

- https://developers.maxon.net/docs/zbrush/py/2026_1_0/index.html
- https://developers.maxon.net/docs/zbrush/py/2026_1_0/manuals/index.html
- https://developers.maxon.net/docs/zbrush/py/2026_1_0/manuals/quickstart.html
- https://developers.maxon.net/docs/zbrush/py/2026_1_0/manuals/api_overview.html
- https://developers.maxon.net/docs/zbrush/py/2026_1_0/manuals/style_guide.html
- https://developers.maxon.net/docs/zbrush/py/2026_1_0/manuals/editor_config.html
- https://developers.maxon.net/docs/zbrush/py/2026_1_0/manuals/importing_libraries.html
- https://developers.maxon.net/docs/zbrush/py/2026_1_0/manuals/python_environment.html
- https://developers.maxon.net/docs/zbrush/py/2026_1_0/api/zbr_cmds_gui.html
- https://developers.maxon.net/docs/zbrush/py/2026_1_0/api/zbr_cmds_modeling.html
- https://developers.maxon.net/docs/zbrush/py/2026_1_0/api/zbr_cmds_system.html
- https://developers.maxon.net/docs/zbrush/py/2026_1_0/examples/index.html
- https://developers.maxon.net/docs/zbrush/py/2026_1_0/examples/ex_hello_world.html
- https://developers.maxon.net/docs/zbrush/py/2026_1_0/examples/gui_ex_gui_notes.html
- https://developers.maxon.net/docs/zbrush/py/2026_1_0/examples/gui_ex_gui_palette.html
- https://developers.maxon.net/docs/zbrush/py/2026_1_0/examples/gui_ex_gui_zscript_port.html
- https://developers.maxon.net/docs/zbrush/py/2026_1_0/examples/gui_ex_gui_notebar.html
- https://developers.maxon.net/docs/zbrush/py/2026_1_0/examples/modeling_ex_mod_curve_lightning.html
- https://developers.maxon.net/docs/zbrush/py/2026_1_0/examples/modeling_ex_mod_subtool_array.html
- https://developers.maxon.net/docs/zbrush/py/2026_1_0/examples/modeling_ex_mod_subtool_export.html
- https://developers.maxon.net/docs/zbrush/py/2026_1_0/examples/modeling_lib_zb_math.html
- https://developers.maxon.net/docs/zbrush/py/2026_1_0/examples/system_ex_sys_timeline_camera.html
- https://developers.maxon.net/docs/zbrush/py/2026_1_0/examples/system_ex_sys_timeline_colors.html
- https://developers.maxon.net/docs/zbrush/py/2026_1_0/misc/changes.html

## Manuals Index (Topics)

- Workflow manuals: Quickstart, API Overview, Importing Libraries, Migrating ZScript.
- Technical manuals: Python Environment, Style Guide, Editor Configuration.

## Python Runtime and VM Facts

- ZBrush 2026.1.0 Python runtime is based on CPython 3.11.9.
- The Python VM is embedded in ZBrush and is persistent for the lifetime of ZBrush.
- The VM is shared across scripts and plugins; state persists between runs.
- sys.executable points to ZBrush.exe or ZBrush.app/Contents/MacOS/ZBrush.
- Standard output and error are redirected to the ZBrush console with a custom stream handler.

## Environment Variables

### PYTHONPATH

- Behaves similarly to standard CPython for module search paths.
- ZBrush scans all PYTHONPATH directories for init.py and executes them on startup.
- This enables a plugin layout with an init.py entry point.

### ZBRUSH_PLUGIN_PATH

- Similar to PYTHONPATH but executes all *.py found in the defined directories on startup.

## Quickstart Facts

### Scripting Interface

- The Python entry point is the ZScript palette.
- The Python Scripting sub-palette exposes Python scripting commands.
- The Script Window Mode sub-palette enables the Python console output.
- Tutorial View is the UI region that contains the console and is toggled by the arrow at the bottom right.

### Running Scripts

- Load: runs a Python script file immediately.
- Reload: reruns the last loaded Python script.
- Command line: ZBrush.exe -script "full\path\script.py" "arg1" "scene_file.ZPR".
- The ZBrush file to load is the last argument on the command line.
- Plugins: scripts can run on startup when placed in plugin search paths.

### Recording Scripts

- Python scripts can be recorded via the Python Scripting sub-palette.
- New Macro starts recording; End Macro stops and saves.
- Loading a recorded macro creates a button in the console that runs the macro when clicked.

### Writing Scripts

- Scripts are .py files.
- Example pattern uses main() and a main guard.
- Example uses zbrush.commands and uses zbc.config(2026) to set configuration state.

## Style Guide (Conventions and Best Practices)

### Line Length

- SDK follows PEP 8 but uses 100 as a line length for docs.
- Recommended line length for user code is 120.

### Type Hinting

- SDK uses Python 3.10/3.11 type hint features (PEP 484, PEP 585, PEP 604).
- Type hints are optional and not enforced at runtime.
- Uses | for unions, list[str] for collections, Callable and Iterator for callable and iterator types.

### Comprehensions

- Used frequently but limited to simple cases.

### Walrus Operator

- Used to assign within expressions; type hints must be declared outside the expression.

### Shared Environment Best Practices

- Avoid altering shared builtin module state (sys, math, random).
- Do not clear sys.modules.
- Avoid overwriting sys.stdin, sys.stdout, sys.stderr.
- Do not spawn new Python processes with multiprocessing or subprocess for the ZBrush VM.
- Working directory is the ZBrush application directory; do not change it.
- Use absolute paths or paths relative to the script directory.

## Editor Configuration (VS Code)

- Recommended tools: VS Code, Python extension, Pylance, autopep8.
- Configure python.analysis.extraPaths to the ZBrush SDK api path for autocompletion.
- Optional: autopep8 formatter with max line length 120 and editor ruler at 120.
- Use 4 spaces for indentation.
- Enable GitHub Copilot for Python.

## Importing Libraries (Three Strategies)

### Local Dependencies

- Place dependencies in a libs folder beside the plugin.
- Add libs directory to sys.path before importing.
- Clean up sys.path after importing.
- Complex approach isolates module objects in sys.modules to avoid conflicts.
- Simple approach only isolates sys.path; use unique module names to avoid collisions.
- Local dependency drawbacks: conflicts, duplication, nested dependency handling, complex packages.

### Global Dependencies

- Copy dependencies to a global module search path.
- Simplest for a single-owner environment but shares versions across plugins.
- Cannot use different library versions across plugins.

### External Package Manager

- ZBrush is not shipped with pip and cannot install pip in-process.
- Use external Python 3.11.9 to install packages to a known path.
- Add that path to sys.path at runtime and remove after import.
- Recommended dedicated path: ZBrush/ZData/Python/site-packages.

## API Overview (General)

### API Style

- API is procedural and GUI-centered.
- Interactions typically replicate user GUI actions.

### Basic Features

- No atomic vector, matrix, color types in the API itself.
- Colors are represented as ints, computed by R * 65536 + G * 256 + B or zbrush.commands.rgb.
- SDK examples provide a Vector helper class (not part of the API).

### Modeling Features (Limits)

- Brushes: no API representation, only UI manipulation.
- Curves: write access only; existing curves cannot be read.
- Tools: very limited read access via query_mesh3d; no vertex/normal/uv access.
- Strokes: read and write access, but creation is via recorded data; cannot be programmatically synthesized.
- ZSpheres: full read and write access.

### GUI Concepts

- Palettes are top-level menu items and containers.
- Sub-palettes group controls within palettes.
- Notes and messages are modal dialogs.
- Item paths are composed from UI labels with colon separators.
- Item paths are case-insensitive and ignore spaces.
- Picker items can be accessed by name even when not visible.
- Empty item path refers to the Tutorial View.

## GUI API (zbrush.commands)

### Signatures: Create

- add_button
- add_note_button
- add_note_switch
- add_palette
- add_slider
- add_subpalette
- add_switch
- close
- delete_interface_item
- show_note

### Signatures: Dialogs

- ask_filename
- ask_string
- message_ok
- message_ok_cancel
- message_yes_no
- message_yes_no_cancel

### Signatures: Getters

- exists
- get
- get_canvas_pan
- get_canvas_zoom
- get_flags
- get_from_note
- get_height
- get_hotkey
- get_id
- get_info
- get_left_mouse_button_state
- get_max
- get_min
- get_mod
- get_mouse_pos
- get_pos
- get_secondary
- get_status
- get_title
- get_width
- is_disabled
- is_enabled
- is_locked
- is_unlocked

### Signatures: Setters

- set
- set_canvas_pan
- set_canvas_zoom
- set_color
- set_hotkey
- set_max
- set_min
- set_mod
- set_notebar_text
- set_status

### Signatures: Interaction

- canvas_click
- click
- disable
- enable
- freeze
- hide
- lock
- maximize
- minimize
- press
- reset
- show
- show_actions
- stroke
- toggle
- un_press
- unlock
- update

### GUI API Facts

- add_button callback signature is f(sender: str) -> None.
- add_slider callback signature is f(sender: str, value: float) -> None.
- add_switch callback signature is f(sender: str, value: bool) -> None.
- add_note_button and add_note_switch define controls for the next show_note.
- show_note returns the index of the pressed button.
- set applies to primary and secondary numeric values; booleans are floats.
- set_status, enable, disable only apply to script-generated items.
- lock and unlock can apply to script and built-in items.
- reset(version) resets UI state; config(version) loads a configuration without user interaction.
- ask_filename supports multiple extensions using Label (*.ext)|*.ext format.
- ZBrush console renders backslashes incorrectly in strings.

## Modeling API (zbrush.commands)

### Signatures: Curves

- add_curve_point
- add_new_curve
- curves_to_ui
- delete_curves
- new_curves

### Signatures: Misc

- create_displacement_map
- create_normal_map
- get_polymesh3d_area
- get_polymesh3d_volume
- is_polymesh3d_solid
- pixol_pick
- query_mesh3d

### Signatures: Strokes

- Stroke
- Strokes
- canvas_stroke
- canvas_strokes
- get_stroke_info
- get_last_stroke
- load_stroke
- load_strokes

### Signatures: Tools and Subtools

- get_active_subtool_index
- get_active_tool_index
- get_active_tool_path
- get_subtool_count
- get_subtool_folder_index
- get_subtool_folder_name
- get_subtool_id
- get_subtool_status
- get_tool_count
- get_tool_path
- locate_subtool
- locate_subtool_by_name
- select_subtool
- select_tool
- set_subtool_status
- set_tool_path

### Signatures: Transforms

- get_transform
- get_transpose
- is_transpose_shown
- set_transform
- set_transpose

### Signatures: ZSpheres

- add_zsphere
- delete_zsphere
- edit_zsphere
- get_zsphere
- set_zsphere

### Modeling API Facts

- Curves must be committed to the UI using curves_to_ui.
- query_mesh3d returns mesh and UV information, with property and index codes.
- get_transform returns a 9-element list for position, scale, rotation in degrees.
- set_transform uses canvas space and degrees.
- ZSphere editing must be done within edit_zsphere.

## System API (zbrush.commands, zbrush.utils, zbrush.zscript_compatibility)

### Signatures: Files

- get_last_typed_filename
- get_last_used_filename
- get_next_filename
- increment_filename
- make_filename
- resolve_path
- set_next_filename

### Signatures: Misc

- config
- interpolate
- randomize
- rgb
- system_info
- zbrush_info
- zscript_compatibility.rand
- zscript_compatibility.rand_int

### Signatures: Python

- utils.run_path
- utils.run_script
- utils.clear_output

### Signatures: Timeline

- delete_keyframe
- get_active_track_index
- get_keyframe_time
- get_keyframes_count
- get_timeline_time
- new_keyframe
- set_active_track_index
- set_keyframe_time
- set_timeline_time
- set_timeline_to_keyframe_time

### System API Facts

- resolve_path resolves a path relative to the executing Python module.
- increment_filename and make_filename exist for legacy ZScript purposes.
- zbrush_info provides system and session values by numeric index.
- Timeline APIs use normalized document time in [0, 1].
- utils.run_path and utils.run_script execute code; running untrusted code is unsafe.
- The console renders backslashes incorrectly; paths are still correct.

## Examples (Factual Summary)

### Example hello_world

- Uses zbc.config(2026), selects Cube3D, converts to PolyMesh3D.
- Applies a recorded Stroke via canvas_stroke.
- Enables edit mode and sets transform rotation.
- Uses a main guard.

### Example gui_palette

- Builds a palette and subpalettes.
- Uses add_button, add_slider, add_switch and callback functions.
- Demonstrates width usage: auto, relative, fixed.
- Uses maximize to unfold a palette.

### Example gui_notes

- Builds a modal note dialog with add_note_button in a loop.
- Uses show_note to retrieve which control was pressed.
- Uses freeze to run a note interface.
- Demonstrates platform-specific path prefix on macOS ("!:").

### Example gui_zscript_port

- A literal ZScript port for notes; not recommended for modern note code.
- Uses show_note return codes for navigation.

### Example gui_notebar

- Uses set_notebar_text to show progress.
- Clears the notebar after finishing.

### Example mod_curve_lightning

- Demonstrates curve creation and value noise.
- Uses local library import and then cleans sys.path and sys.modules.
- Requires an editable PolyMesh3D and CurveTube brush.

### Example mod_subtool_array

- Shows tool selection by item path (Tool:Name).
- Creates an array of subtools by duplicating and setting Tool:Geometry positions.
- Uses set_color and Color:FillObject.

### Example mod_subtool_export

- Command-line execution with -script and extra arguments.
- Uses set_next_filename and presses Tool:Export for OBJ.
- Uses ask_filename when export directory is not provided.

### Example lib_zb_math

- Provides Vector and ValueNoise helpers used by modeling examples.
- Not part of the ZBrush API and not a supported feature.

### Example sys_timeline_camera

- Uses timeline tracks and keyframes to create a camera turntable.
- Uses query_mesh3d to compute bounds and scale factor.
- Animates transform rotation and sets keyframes with normalized time.

### Example sys_timeline_colors

- Uses timeline color track to create keyframes.
- Explains normalized document time and uses Movie:TimeLine:Duration.

## Changes in 2026.1

- Documentation layout updated and API documentation completed.
- Manuals and code examples added.
- No API changes listed.
