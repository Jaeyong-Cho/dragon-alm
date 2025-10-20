from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QLineEdit
)
from PyQt6.QtCore import Qt
from typing import List, Set
from models.design import Design


class DesignSelectorDialog(QDialog):
    """Dialog for selecting designs to link"""

    def __init__(self, parent=None, designs: List[Design] = None, selected_design_ids: Set[int] = None):
        """
        Initialize dialog

        Args:
            parent: Parent widget
            designs: List of available designs
            selected_design_ids: Set of currently selected design IDs
        """
        super().__init__(parent)
        self.designs = designs or []
        self.selected_design_ids = selected_design_ids or set()
        
        self.setWindowTitle("Select Designs")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        self._init_ui()
        self._populate_list()

    def _init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)
        
        # Info label
        info_label = QLabel("Select designs to link with this requirement:")
        layout.addWidget(info_label)
        
        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter by name or type...")
        self.search_input.textChanged.connect(self._filter_designs)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Design list
        self.design_list = QListWidget()
        self.design_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        layout.addWidget(self.design_list)
        
        # Selection info
        self.selection_label = QLabel()
        self._update_selection_label()
        layout.addWidget(self.selection_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.select_all_button = QPushButton("Select All")
        self.select_all_button.clicked.connect(self._select_all)
        
        self.clear_button = QPushButton("Clear All")
        self.clear_button.clicked.connect(self._clear_all)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setDefault(True)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.select_all_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Connect selection change
        self.design_list.itemSelectionChanged.connect(self._update_selection_label)

    def _populate_list(self):
        """Populate the design list"""
        self.design_list.clear()
        
        for design in self.designs:
            item_text = f"{design.name} [{design.type}] - {design.status}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, design.id)
            
            # Select if previously selected
            if design.id in self.selected_design_ids:
                item.setSelected(True)
            
            self.design_list.addItem(item)

    def _filter_designs(self, text: str):
        """Filter designs based on search text"""
        text_lower = text.lower()
        
        for i in range(self.design_list.count()):
            item = self.design_list.item(i)
            item_text = item.text().lower()
            item.setHidden(text_lower not in item_text)

    def _select_all(self):
        """Select all visible items"""
        for i in range(self.design_list.count()):
            item = self.design_list.item(i)
            if not item.isHidden():
                item.setSelected(True)

    def _clear_all(self):
        """Clear all selections"""
        self.design_list.clearSelection()

    def _update_selection_label(self):
        """Update the selection count label"""
        count = len(self.design_list.selectedItems())
        self.selection_label.setText(f"Selected: {count} design(s)")

    def get_selected_design_ids(self) -> Set[int]:
        """
        Get selected design IDs

        Returns:
            Set of selected design IDs
        """
        selected_ids = set()
        for item in self.design_list.selectedItems():
            design_id = item.data(Qt.ItemDataRole.UserRole)
            if design_id is not None:
                selected_ids.add(design_id)
        return selected_ids

    def get_selected_designs(self) -> List[Design]:
        """
        Get selected design objects

        Returns:
            List of selected designs
        """
        selected_ids = self.get_selected_design_ids()
        return [d for d in self.designs if d.id in selected_ids]
