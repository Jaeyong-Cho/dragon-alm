from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QComboBox, QPushButton,
    QFormLayout, QListWidget, QAbstractItemView,
    QTabWidget, QSplitter, QWidget
)
from PyQt6.QtCore import Qt
from typing import Optional, List
from models.design import Design
from ui.widgets.markdown_viewer import MarkdownViewer


class DesignDialog(QDialog):
    """Dialog for creating/editing designs"""

    DESIGN_TYPES = ["Architecture", "Component", "Interface", "Database", "Algorithm", "Security"]
    STATUSES = ["Draft", "In Review", "Approved", "Implemented"]

    def __init__(self, parent=None, design: Optional[Design] = None, requirements: List = None):
        super().__init__(parent)
        self.design = design
        self.requirements = requirements or []
        self.setWindowTitle("Edit Design" if design else "New Design")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.init_ui()

        if design:
            self.load_design_data()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)

        # Form layout
        form = QFormLayout()

        # Name
        self.name_edit = QLineEdit()
        form.addRow("Name:", self.name_edit)

        # Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(self.DESIGN_TYPES)
        form.addRow("Type:", self.type_combo)

        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(self.STATUSES)
        form.addRow("Status:", self.status_combo)

        layout.addLayout(form)

        # Description with markdown support
        desc_label = QLabel("Description (Markdown supported):")
        layout.addWidget(desc_label)

        # Create splitter for editor and preview
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Editor side
        editor_widget = QTabWidget()

        self.description_edit = QTextEdit()
        self.description_edit.setMinimumHeight(200)
        self.description_edit.setPlaceholderText(
            "Enter description in Markdown format...\n\n"
            "Supported features:\n"
            "- Headers: # H1, ## H2, ### H3\n"
            "- Lists: - item or 1. item\n"
            "- Code: `inline` or ```language block```\n"
            "- PlantUML: ```plantuml ... ```\n"
            "- Tables, links, images, etc."
        )
        editor_widget.addTab(self.description_edit, "Edit")

        splitter.addWidget(editor_widget)

        # Preview side
        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        
        # Refresh button
        refresh_button = QPushButton("Refresh Preview")
        refresh_button.clicked.connect(self._update_preview)
        preview_layout.addWidget(refresh_button)
        
        self.markdown_preview = MarkdownViewer()
        preview_layout.addWidget(self.markdown_preview)
        
        preview_widget = QTabWidget()
        preview_widget.addTab(preview_container, "Preview")

        splitter.addWidget(preview_widget)
        splitter.setSizes([400, 400])

        layout.addWidget(splitter)

        # Requirements section
        req_label = QLabel("Linked Requirements:")
        layout.addWidget(req_label)

        self.requirements_list = QListWidget()
        self.requirements_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.requirements_list.setMaximumHeight(120)

        # Populate requirements
        for req in self.requirements:
            item_text = f"REQ-{req.id}: {req.title}"
            self.requirements_list.addItem(item_text)
            item = self.requirements_list.item(self.requirements_list.count() - 1)
            item.setData(Qt.ItemDataRole.UserRole, req.id)

        layout.addWidget(self.requirements_list)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        save_button.setDefault(True)
        button_layout.addWidget(save_button)

        layout.addLayout(button_layout)

    def _update_preview(self):
        """Update markdown preview"""
        markdown_text = self.description_edit.toPlainText()
        self.markdown_preview.set_markdown(markdown_text)

    def load_design_data(self):
        """Load existing design data into the form"""
        self.name_edit.setText(self.design.name)
        self.description_edit.setText(self.design.description)
        self._update_preview()

        # Set type
        type_index = self.type_combo.findText(self.design.type)
        if type_index >= 0:
            self.type_combo.setCurrentIndex(type_index)

        # Set status
        status_index = self.status_combo.findText(self.design.status)
        if status_index >= 0:
            self.status_combo.setCurrentIndex(status_index)

        # Select linked requirements
        for i in range(self.requirements_list.count()):
            item = self.requirements_list.item(i)
            req_id = item.data(Qt.ItemDataRole.UserRole)
            if req_id in self.design.requirement_ids:
                item.setSelected(True)

    def get_data(self) -> dict:
        """Get the form data"""
        # Get selected requirement IDs
        selected_req_ids = []
        for item in self.requirements_list.selectedItems():
            req_id = item.data(Qt.ItemDataRole.UserRole)
            selected_req_ids.append(req_id)

        return {
            'name': self.name_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip(),
            'type': self.type_combo.currentText(),
            'status': self.status_combo.currentText(),
            'requirement_ids': selected_req_ids
        }

    def accept(self):
        """Validate and accept the dialog"""
        data = self.get_data()

        if not data['name']:
            self.name_edit.setFocus()
            return

        if not data['description']:
            self.description_edit.setFocus()
            return

        super().accept()
