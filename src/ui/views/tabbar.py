from PyQt6.QtWidgets import QTabBar, QStylePainter, QStyleOptionTab, QStyle
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPalette, QColor


class TabBar(QTabBar):
    """Custom TabBar with enhanced styling and functionality"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()

    def _setup_style(self):
        """Setup the tab bar style"""
        self.setDrawBase(False)
        self.setExpanding(False)
        self.setDocumentMode(True)
        
        # Set tab shape
        self.setShape(QTabBar.Shape.RoundedNorth)
        
        # # Apply custom stylesheet
        # self.setStyleSheet("""
        #     QTabBar::tab {
        #         background: #f0f0f0;
        #         color: #333333;
        #         padding: 10px 20px;
        #         margin-right: 2px;
        #         border-top-left-radius: 4px;
        #         border-top-right-radius: 4px;
        #         min-width: 100px;
        #     }
            
        #     QTabBar::tab:selected {
        #         background: #ffffff;
        #         color: #000000;
        #         font-weight: bold;
        #         border-bottom: 2px solid #0078d4;
        #     }
            
        #     QTabBar::tab:hover:!selected {
        #         background: #e8e8e8;
        #     }
            
        #     QTabBar::tab:disabled {
        #         color: #999999;
        #     }
        # """)

    def set_tab_enabled(self, index: int, enabled: bool):
        """Enable or disable a specific tab"""
        self.setTabEnabled(index, enabled)

    def set_tab_icon(self, index: int, icon):
        """Set an icon for a specific tab"""
        self.setTabIcon(index, icon)

    def set_tab_tooltip(self, index: int, tooltip: str):
        """Set a tooltip for a specific tab"""
        self.setTabToolTip(index, tooltip)
