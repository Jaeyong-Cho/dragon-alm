from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QPushButton,
    QLabel, QMessageBox, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt
from typing import Optional, Dict, Any, List, Set
from models.requirement import Requirement
from models.design import Design
from models.enums import RequirementStatus, Priority
from ui.dialogs.design_selector_dialog import DesignSelectorDialog


class RequirementDialog(QDialog):
    """Dialog for creating/editing requirements"""

    def __init__(self, parent=None, requirement: Optional[Requirement] = None, 
                 available_designs: Optional[List[Design]] = None):
        """
        Initialize dialog

        Args:
            parent: Parent widget
            requirement: Existing requirement for editing (None for create)
            available_designs: List of available designs for linking
        """
        super().__init__(parent)
        self.requirement = requirement
        self.is_edit_mode = requirement is not None
        self.available_designs = available_designs or []
        self.selected_design_ids: Set[int] = set()

        self.setWindowTitle("Edit Requirement" if self.is_edit_mode else "Create Requirement")
        self.setMinimumWidth(600)
        self.setMinimumHeight(550)

        self._init_ui()

        if self.is_edit_mode:
            self._populate_fields()

    def _init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)

        # Form layout
        form_layout = QFormLayout()

        # ID field (read-only in edit mode)
        self.id_input = QLineEdit()
        if self.is_edit_mode:
            self.id_input.setReadOnly(True)
            self.id_input.setStyleSheet("background-color: #f0f0f0;")
        else:
            self.id_input.setPlaceholderText("Auto-generated if empty")
        form_layout.addRow("ID:", self.id_input)

        # Title field
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter requirement title")
        self.title_input.setMaxLength(200)
        form_layout.addRow("Title *:", self.title_input)

        # Status field
        self.status_combo = QComboBox()
        self.status_combo.addItems([status.value for status in RequirementStatus])
        form_layout.addRow("Status:", self.status_combo)

        # Priority field
        self.priority_combo = QComboBox()
        self.priority_combo.addItems([priority.value for priority in Priority])
        self.priority_combo.setCurrentText(Priority.MEDIUM.value)
        form_layout.addRow("Priority:", self.priority_combo)

        # Category field
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Enter category (optional)")
        self.category_input.setMaxLength(50)
        form_layout.addRow("Category:", self.category_input)

        # Design Trace field with button
        design_trace_layout = QHBoxLayout()
        self.design_trace_display = QListWidget()
        self.design_trace_display.setMaximumHeight(80)
        self.design_trace_display.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        
        design_trace_button_layout = QVBoxLayout()
        self.design_selector_button = QPushButton("→")
        self.design_selector_button.setFixedWidth(40)
        self.design_selector_button.setToolTip("Select designs to link")
        self.design_selector_button.clicked.connect(self._open_design_selector)
        design_trace_button_layout.addWidget(self.design_selector_button)
        design_trace_button_layout.addStretch()
        
        design_trace_layout.addWidget(self.design_trace_display)
        design_trace_layout.addLayout(design_trace_button_layout)
        form_layout.addRow("Linked Designs:", design_trace_layout)

        # Description field
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter detailed description")
        self.description_input.setMinimumHeight(150)
        form_layout.addRow("Description:", self.description_input)

        # Verification criteria field
        self.verification_input = QTextEdit()
        self.verification_input.setPlaceholderText("Enter verification criteria (optional)")
        self.verification_input.setMinimumHeight(100)
        form_layout.addRow("Verification Criteria:", self.verification_input)

        layout.addLayout(form_layout)

        # Required field note
        note_label = QLabel("* Required fields")
        note_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(note_label)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_button = QPushButton("Update" if self.is_edit_mode else "Create")
        self.save_button.clicked.connect(self._on_save)
        self.save_button.setDefault(True)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def _populate_fields(self):
        """Populate fields with existing requirement data"""
        if self.requirement:
            self.id_input.setText(self.requirement.id)
            self.title_input.setText(self.requirement.title)
            self.status_combo.setCurrentText(self.requirement.status.value)
            self.priority_combo.setCurrentText(self.requirement.priority.value)
            self.category_input.setText(self.requirement.category)
            self.description_input.setPlainText(self.requirement.description)
            self.verification_input.setPlainText(self.requirement.verification_criteria)
            
            # Load linked designs if the requirement has design_ids
            if hasattr(self.requirement, 'design_ids') and self.requirement.design_ids:
                self.selected_design_ids = set(self.requirement.design_ids)
                self._update_design_display()

    def _open_design_selector(self):
        """Open design selector dialog"""
        dialog = DesignSelectorDialog(
            self, 
            self.available_designs, 
            self.selected_design_ids
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.selected_design_ids = dialog.get_selected_design_ids()
            self._update_design_display()

    def _update_design_display(self):
        """Update the design display list"""
        self.design_trace_display.clear()
        
        # Find and display selected designs
        selected_designs = [d for d in self.available_designs if d.id in self.selected_design_ids]
        
        for design in selected_designs:
            item_text = f"{design.name} [{design.type}]"
            item = QListWidgetItem(item_text)
            self.design_trace_display.addItem(item)
        
        if not selected_designs:
            item = QListWidgetItem("(No designs linked)")
            item.setForeground(Qt.GlobalColor.gray)
            self.design_trace_display.addItem(item)

    def _on_save(self):
        """Handle save button click"""
        # Validate required fields
        if not self.title_input.text().strip():
            QMessageBox.warning(
                self,
                "Validation Error",
                "Title is required"
            )
            self.title_input.setFocus()
            return

        self.accept()

    def get_data(self) -> Dict[str, Any]:
        """
        Get form data as dictionary

        Returns:
            Dictionary with requirement data
        """
        data = {
            'title': self.title_input.text().strip(),
            'description': self.description_input.toPlainText().strip(),
            'status': self.status_combo.currentText(),
            'priority': self.priority_combo.currentText(),
            'category': self.category_input.text().strip(),
            'verification_criteria': self.verification_input.toPlainText().strip(),
            'design_ids': list(self.selected_design_ids)
        }

        if self.id_input.text().strip():
            data['id'] = self.id_input.text().strip()

        return data
