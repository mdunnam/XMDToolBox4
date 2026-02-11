"""XMD ToolBox dark theme stylesheet.

Premium dark-mode QSS inspired by professional DCC tooling.
Surfaces use layered charcoal tones; accent is warm saturated orange.

Design tokens
─────────────
Typography:  13px base, 11px caption/secondary, 15px heading
Spacing:     4px unit — 4 · 8 · 12 · 16 · 20
Radii:       6px small (items), 10px medium (cards/inputs), 14px large (floating)
"""

# ---------------------------------------------------------------------------
# Palette tokens (referenced in the stylesheet string below)
# ---------------------------------------------------------------------------
# Surface hierarchy (darkest → lightest)
_BG_BASE      = "#0D0D10"   # App background — nearly black
_BG_SURFACE   = "#161619"   # Panel / card background
_BG_RAISED    = "#1E1E22"   # Raised elements (buttons, inputs)
_BG_HOVER     = "#26262A"   # Hover state
_BG_PRESSED   = "#303035"   # Pressed state
_BG_DOCK_AREA = "#111114"   # Dock area overlay

# Text
_TEXT_PRIMARY   = "#E8E8EC"
_TEXT_SECONDARY = "#7A7A80"
_TEXT_DISABLED  = "#454548"

# Accent — warm saturated orange
_ACCENT         = "#E8652B"
_ACCENT_HOVER   = "#F07A42"
_ACCENT_PRESSED = "#CC5520"
_ACCENT_DIM     = "#2D1A10"  # Subtle accent tint for selections

# Borders / separators
_BORDER_SUBTLE = "#1D1D21"
_BORDER_INPUT  = "#2C2C30"

# Misc
_SCROLLBAR_BG  = "#111114"
_SCROLLBAR_FG  = "#2C2C30"
_TOOLTIP_BG    = "#1E1E22"

# Spacing scale (4px unit)
_SP_XS  = "4px"
_SP_SM  = "8px"
_SP_MD  = "12px"
_SP_LG  = "16px"
_SP_XL  = "20px"

# Radii
_R_SM  = "6px"
_R_MD  = "10px"
_R_LG  = "14px"

# Typography
_FONT_BASE    = "13px"
_FONT_CAPTION = "11px"
_FONT_HEADING = "15px"

STYLESHEET = f"""
/* ================================================================
   GLOBAL
   ================================================================ */
* {{
    font-family: "Segoe UI Variable", "Segoe UI", "Inter", "Roboto", sans-serif;
    font-size: {_FONT_BASE};
    color: {_TEXT_PRIMARY};
    outline: none;
}}

QMainWindow {{
    background: {_BG_BASE};
}}

QWidget {{
    background: {_BG_BASE};
    border: none;
}}

/* ================================================================
   MENU BAR
   ================================================================ */
QMenuBar {{
    background: {_BG_SURFACE};
    padding: {_SP_XS} {_SP_SM};
    border-bottom: 1px solid {_BORDER_SUBTLE};
    font-size: {_FONT_BASE};
}}
QMenuBar::item {{
    padding: {_SP_SM} {_SP_MD};
    border-radius: {_R_SM};
    color: {_TEXT_SECONDARY};
}}
QMenuBar::item:selected {{
    background: {_BG_HOVER};
    color: {_TEXT_PRIMARY};
}}
QMenu {{
    background: {_BG_RAISED};
    border: 1px solid {_BORDER_SUBTLE};
    border-radius: {_R_MD};
    padding: {_SP_XS} 0;
}}
QMenu::item {{
    padding: {_SP_SM} {_SP_XL} {_SP_SM} {_SP_MD};
    border-radius: {_R_SM};
    margin: 1px {_SP_XS};
}}
QMenu::item:selected {{
    background: {_ACCENT_DIM};
    color: {_ACCENT};
}}
QMenu::separator {{
    height: 1px;
    background: {_BORDER_SUBTLE};
    margin: {_SP_XS} {_SP_SM};
}}

/* ================================================================
   TOOLBAR
   ================================================================ */
QToolBar {{
    background: {_BG_SURFACE};
    border: none;
    spacing: {_SP_XS};
    padding: {_SP_XS} {_SP_SM};
    border-bottom: 1px solid {_BORDER_SUBTLE};
}}
QToolBar::separator {{
    width: 1px;
    background: {_BORDER_SUBTLE};
    margin: {_SP_XS} {_SP_SM};
}}
QToolButton {{
    background: transparent;
    border: none;
    border-radius: {_R_SM};
    padding: {_SP_SM} {_SP_MD};
    color: {_TEXT_SECONDARY};
    font-size: {_FONT_BASE};
    font-weight: 500;
}}
QToolButton:hover {{
    background: {_BG_HOVER};
    color: {_TEXT_PRIMARY};
}}
QToolButton:pressed {{
    background: {_BG_PRESSED};
}}

/* ================================================================
   TAB WIDGET (fallback — QtAds overrides below)
   ================================================================ */
QTabWidget::pane {{
    background: {_BG_SURFACE};
    border: none;
    border-radius: {_R_MD};
    top: -1px;
}}
QTabBar {{
    background: transparent;
}}
QTabBar::tab {{
    background: transparent;
    color: {_TEXT_SECONDARY};
    padding: {_SP_SM} {_SP_LG};
    margin-right: 2px;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: {_FONT_BASE};
    font-weight: 500;
}}
QTabBar::tab:hover {{
    color: {_TEXT_PRIMARY};
    background: {_BG_HOVER};
    border-radius: {_R_SM} {_R_SM} 0 0;
}}
QTabBar::tab:selected {{
    color: {_ACCENT};
    border-bottom: 2px solid {_ACCENT};
}}

/* ================================================================
   BUTTONS
   ================================================================ */
QPushButton {{
    background: {_BG_RAISED};
    color: {_TEXT_PRIMARY};
    border: none;
    border-radius: {_R_MD};
    padding: {_SP_SM} {_SP_LG};
    font-size: {_FONT_BASE};
    font-weight: 500;
    min-height: 20px;
}}
QPushButton:hover {{
    background: {_BG_HOVER};
}}
QPushButton:pressed {{
    background: {_BG_PRESSED};
}}
QPushButton:disabled {{
    color: {_TEXT_DISABLED};
    background: {_BG_SURFACE};
}}
/* Primary / accent button (use setProperty("accent", True) in code) */
QPushButton[accent="true"] {{
    background: {_ACCENT};
    color: #FFFFFF;
}}
QPushButton[accent="true"]:hover {{
    background: {_ACCENT_HOVER};
}}
QPushButton[accent="true"]:pressed {{
    background: {_ACCENT_PRESSED};
}}
/* Checkable push buttons (favorites, toggles) */
QPushButton:checked {{
    background: {_ACCENT_DIM};
    color: {_ACCENT};
}}

/* ================================================================
   LINE EDIT / TEXT EDIT / COMBO BOX
   ================================================================ */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background: {_BG_RAISED};
    color: {_TEXT_PRIMARY};
    border: 1px solid {_BORDER_INPUT};
    border-radius: {_R_MD};
    padding: {_SP_SM} {_SP_MD};
    font-size: {_FONT_BASE};
    selection-background-color: {_ACCENT_DIM};
    selection-color: {_ACCENT};
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1px solid {_ACCENT};
}}
QLineEdit:disabled, QTextEdit:disabled {{
    color: {_TEXT_DISABLED};
    background: {_BG_SURFACE};
}}

QComboBox {{
    background: {_BG_RAISED};
    color: {_TEXT_PRIMARY};
    border: 1px solid {_BORDER_INPUT};
    border-radius: {_R_MD};
    padding: {_SP_SM} {_SP_MD};
    font-size: {_FONT_BASE};
    min-height: 20px;
}}
QComboBox:hover {{
    border: 1px solid {_ACCENT};
}}
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border: none;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {_TEXT_SECONDARY};
    margin-right: {_SP_SM};
}}
QComboBox QAbstractItemView {{
    background: {_BG_RAISED};
    color: {_TEXT_PRIMARY};
    border: 1px solid {_BORDER_SUBTLE};
    border-radius: {_R_MD};
    selection-background-color: {_ACCENT_DIM};
    selection-color: {_ACCENT};
    padding: {_SP_XS};
}}

/* ================================================================
   GROUP BOX
   ================================================================ */
QGroupBox {{
    background: {_BG_SURFACE};
    border: none;
    border-radius: {_R_LG};
    margin-top: {_SP_LG};
    padding: {_SP_XL} {_SP_LG} {_SP_LG} {_SP_LG};
    font-weight: 600;
    font-size: {_FONT_BASE};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: {_SP_XS} {_SP_SM};
    color: {_TEXT_SECONDARY};
    font-size: {_FONT_CAPTION};
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* ================================================================
   LIST / TREE / TABLE
   ================================================================ */
QListWidget, QTreeWidget, QTableWidget, QListView, QTreeView, QTableView {{
    background: {_BG_SURFACE};
    alternate-background-color: {_BG_RAISED};
    border: none;
    border-radius: {_R_MD};
    outline: none;
    font-size: {_FONT_BASE};
}}
QListWidget::item, QTreeWidget::item, QTableWidget::item {{
    padding: {_SP_SM};
    border: none;
    border-radius: {_R_SM};
    margin: 1px {_SP_XS};
}}
QListWidget::item:hover, QTreeWidget::item:hover {{
    background: {_BG_HOVER};
}}
QListWidget::item:selected, QTreeWidget::item:selected {{
    background: {_ACCENT_DIM};
    color: {_ACCENT};
}}
QHeaderView::section {{
    background: {_BG_RAISED};
    color: {_TEXT_SECONDARY};
    border: none;
    padding: {_SP_SM} {_SP_MD};
    font-weight: 600;
    font-size: {_FONT_CAPTION};
    text-transform: uppercase;
}}

/* ================================================================
   SCROLL BARS
   ================================================================ */
QScrollBar:vertical {{
    background: {_SCROLLBAR_BG};
    width: 6px;
    margin: 0;
    border: none;
}}
QScrollBar::handle:vertical {{
    background: {_SCROLLBAR_FG};
    min-height: 30px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical:hover {{
    background: {_TEXT_DISABLED};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: {_SCROLLBAR_BG};
    height: 6px;
    margin: 0;
    border: none;
}}
QScrollBar::handle:horizontal {{
    background: {_SCROLLBAR_FG};
    min-width: 30px;
    border-radius: 3px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {_TEXT_DISABLED};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* ================================================================
   SPLITTER
   ================================================================ */
QSplitter::handle {{
    background: {_BORDER_SUBTLE};
}}
QSplitter::handle:horizontal {{
    width: 2px;
}}
QSplitter::handle:vertical {{
    height: 2px;
}}

/* ================================================================
   TOOLTIPS
   ================================================================ */
QToolTip {{
    background: {_TOOLTIP_BG};
    color: {_TEXT_PRIMARY};
    border: 1px solid {_BORDER_SUBTLE};
    border-radius: {_R_SM};
    padding: {_SP_SM} {_SP_MD};
    font-size: {_FONT_BASE};
}}

/* ================================================================
   LABELS
   ================================================================ */
QLabel {{
    color: {_TEXT_PRIMARY};
    background: transparent;
    font-size: {_FONT_BASE};
}}
QLabel[secondary="true"] {{
    color: {_TEXT_SECONDARY};
    font-size: {_FONT_CAPTION};
}}
QLabel[heading="true"] {{
    font-size: {_FONT_HEADING};
    font-weight: 700;
    color: {_TEXT_PRIMARY};
}}

/* ================================================================
   STATUS BAR
   ================================================================ */
QStatusBar {{
    background: {_BG_SURFACE};
    color: {_TEXT_SECONDARY};
    border-top: 1px solid {_BORDER_SUBTLE};
    font-size: {_FONT_CAPTION};
    padding: {_SP_XS} {_SP_SM};
}}

/* ================================================================
   DOCK WIDGETS  (QtAds overrides)
   ================================================================ */
ads--CDockContainerWidget {{
    background: {_BG_BASE};
}}
ads--CDockAreaWidget {{
    background: {_BG_BASE};
    border: none;
}}
ads--CDockWidget {{
    background: {_BG_BASE};
}}
ads--CDockWidgetTab {{
    background: {_BG_SURFACE};
    border: none;
    padding: 10px 20px;
    color: {_TEXT_SECONDARY};
    border-radius: {_R_SM} {_R_SM} 0 0;
    font-size: {_FONT_BASE};
    font-weight: 500;
    qproperty-iconSize: 32px 32px;
    min-width: 52px;
    min-height: 48px;
}}
ads--CDockWidgetTab:hover {{
    background: {_BG_HOVER};
    color: {_TEXT_PRIMARY};
}}
ads--CDockWidgetTab[activeTab="true"] {{
    background: {_BG_RAISED};
    color: {_ACCENT};
    border-bottom: 2px solid {_ACCENT};
}}
ads--CDockAreaTitleBar {{
    background: {_BG_SURFACE};
    border: none;
    padding: 0 {_SP_XS};
}}
ads--CDockAreaTitleBar > QPushButton {{
    background: transparent;
    border: none;
    padding: {_SP_XS};
    border-radius: {_R_SM};
    min-height: 16px;
}}
ads--CDockAreaTitleBar > QPushButton:hover {{
    background: {_BG_HOVER};
}}
ads--CFloatingDockContainer {{
    background: {_BG_BASE};
    border: 1px solid {_BORDER_SUBTLE};
    border-radius: {_R_LG};
}}
ads--CDockSplitter::handle {{
    background: {_BORDER_SUBTLE};
}}

/* ================================================================
   FORM LAYOUT LABELS
   ================================================================ */
QFormLayout QLabel {{
    color: {_TEXT_SECONDARY};
    font-weight: 500;
    font-size: {_FONT_CAPTION};
    padding-top: {_SP_XS};
}}
"""
