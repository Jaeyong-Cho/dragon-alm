from PyQt6.QtWidgets import QToolBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import pyqtSignal, Qt, QSize


class ToolBar(QToolBar):
    """Main toolbar for the application with common actions."""
    
    # Signals
    save_triggered = pyqtSignal()
    export_triggered = pyqtSignal()
    settings_triggered = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__("Main Toolbar", parent)
        self._setup_ui()
        self._create_actions()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup toolbar UI properties."""
        self.setMovable(False)
        self.setFloatable(False)
        self.setIconSize(QSize(24, 24))
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
    
    def _create_actions(self):
        """Create toolbar actions."""
        # Save Action
        self.save_action = QAction("Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.setStatusTip("Save current work")
        self.addAction(self.save_action)
        
        self.addSeparator()
        
        # Export Action
        self.export_action = QAction("Export", self)
        self.export_action.setShortcut("Ctrl+E")
        self.export_action.setStatusTip("Export data")
        self.addAction(self.export_action)
        
        self.addSeparator()
        
        # Settings Action
        self.settings_action = QAction("Settings", self)
        self.settings_action.setShortcut("Ctrl+,")
        self.settings_action.setStatusTip("Open settings")
        self.addAction(self.settings_action)
        
        # Add spacer to push remaining items to the right
        spacer = QToolBar(self)
        spacer.setFixedWidth(20)
        self.addWidget(spacer)
    
    def _connect_signals(self):
        """Connect action signals to toolbar signals."""
        self.save_action.triggered.connect(self._on_save)
        self.export_action.triggered.connect(self._on_export)
        self.settings_action.triggered.connect(self._on_settings)
    
    def _on_save(self):
        """Handle save action"""
        # TODO: Implement save functionality
        QMessageBox.information(self, "Save", "Save functionality will be implemented")
        self.save_triggered.emit()
    
    def _on_export(self):
        """Handle export action"""
        # TODO: Implement export functionality
        QMessageBox.information(self, "Export", "Export functionality will be implemented")
        self.export_triggered.emit()
    
    def _on_settings(self):
        """Handle settings action"""
        # TODO: Implement settings dialog
        QMessageBox.information(self, "Settings", "Settings dialog will be implemented")
        self.settings_triggered.emit()
    
    def set_save_enabled(self, enabled: bool):
        """Enable or disable the save action."""
        self.save_action.setEnabled(enabled)
    
    def set_export_enabled(self, enabled: bool):
        """Enable or disable the export action."""
        self.export_action.setEnabled(enabled)
    
    def set_icon(self, action_name: str, icon: QIcon):
        """Set icon for a specific action.
        
        Args:
            action_name: Name of the action ('save', 'export', or 'settings')
            icon: QIcon to set for the action
        """
        action_map = {
            'save': self.save_action,
            'export': self.export_action,
            'settings': self.settings_action
        }
        
        if action_name in action_map:
            action_map[action_name].setIcon(icon)
