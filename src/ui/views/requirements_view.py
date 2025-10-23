from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QLineEdit, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import List, Optional
from controllers.requirement_controller import RequirementController
from controllers.design_controller import DesignController
from models.requirement import Requirement
from ui.dialogs.requirement_dialog import RequirementDialog


class RequirementsView(QWidget):
    """View for managing requirements"""

    requirement_selected = pyqtSignal(str)  # Emits requirement ID

    def __init__(self, controller: RequirementController, design_controller: Optional[DesignController] = None, parent=None):
        """
        Initialize view

        Args:
            controller: Requirement controller
            design_controller: Design controller for linking
            parent: Parent widget
        """
        super().__init__(parent)
        self.controller = controller
        self.design_controller = design_controller
        self.controller.add_observer(self.refresh_table)

        self._init_ui()
        self.refresh_table()

    def _init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)

        # Toolbar
        toolbar = QHBoxLayout()

        # Search box
        search_label = QLabel("Search:")
        toolbar.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by ID, title, or description...")
        self.search_input.textChanged.connect(self._on_search)
        self.search_input.setMaximumWidth(300)
        toolbar.addWidget(self.search_input)

        toolbar.addStretch()

        # Action buttons
        self.new_button = QPushButton("New")
        self.new_button.clicked.connect(self._on_new)
        toolbar.addWidget(self.new_button)

        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self._on_edit)
        self.edit_button.setEnabled(False)
        toolbar.addWidget(self.edit_button)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self._on_delete)
        self.delete_button.setEnabled(False)
        toolbar.addWidget(self.delete_button)

        layout.addLayout(toolbar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Title", "Status", "Priority", "Category", "Updated"
        ])

        # Configure table
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)

        # Set column stretch
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        # Connect selection signal
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.table.itemDoubleClicked.connect(self._on_edit)

        layout.addWidget(self.table)

        # Status bar
        self.status_label = QLabel("0 requirements")
        layout.addWidget(self.status_label)

    def refresh_table(self):
        """Refresh table with current requirements"""
        requirements = self.controller.get_all_requirements()
        self._populate_table(requirements)

    def _populate_table(self, requirements: List[Requirement]):
        """Populate table with requirements"""
        self.table.setRowCount(0)

        for req in requirements:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # ID
            id_item = QTableWidgetItem(req.id)
            self.table.setItem(row, 0, id_item)

            # Title
            title_item = QTableWidgetItem(req.title)
            self.table.setItem(row, 1, title_item)

            # Status
            status_item = QTableWidgetItem(req.status.value)
            self.table.setItem(row, 2, status_item)

            # Priority
            priority_item = QTableWidgetItem(req.priority.value)
            self.table.setItem(row, 3, priority_item)

            # Category
            category_item = QTableWidgetItem(req.category)
            self.table.setItem(row, 4, category_item)

            # Updated date
            updated_item = QTableWidgetItem(
                req.updated_at.strftime("%Y-%m-%d %H:%M")
            )
            self.table.setItem(row, 5, updated_item)

        # Update status
        self.status_label.setText(
            f"{len(requirements)} requirement{'s' if len(requirements) != 1 else ''}"
        )

    def _on_selection_changed(self):
        """Handle selection change"""
        has_selection = len(self.table.selectedItems()) > 0
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

        if has_selection:
            req_id = self.table.item(self.table.currentRow(), 0).text()
            self.requirement_selected.emit(req_id)

    def _on_new(self):
        """Handle new requirement button"""
        # Get available designs
        available_designs = []
        if self.design_controller:
            available_designs = self.design_controller.get_all_designs()
        
        dialog = RequirementDialog(self, available_designs=available_designs)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            success, message, requirement = self.controller.create_requirement(data)

            if success:
                QMessageBox.information(self, "Success", message)
                self.refresh_table()
            else:
                QMessageBox.critical(self, "Error", message)

    def _on_edit(self):
        """Handle edit button"""
        if self.table.currentRow() < 0:
            return

        req_id = self.table.item(self.table.currentRow(), 0).text()
        requirement = self.controller.manager.get_requirement(req_id)

        if requirement is None:
            QMessageBox.warning(self, "Error", f"Requirement {req_id} not found")
            return

        # Get available designs
        available_designs = []
        if self.design_controller:
            available_designs = self.design_controller.get_all_designs()

        dialog = RequirementDialog(self, requirement, available_designs)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            success, message, updated_req = self.controller.update_requirement(req_id, data)

            if success:
                QMessageBox.information(self, "Success", message)
                self.refresh_table()
            else:
                QMessageBox.critical(self, "Error", message)

    def _on_delete(self):
        """Handle delete button"""
        if self.table.currentRow() < 0:
            return

        req_id = self.table.item(self.table.currentRow(), 0).text()
        title = self.table.item(self.table.currentRow(), 1).text()

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete requirement '{req_id}: {title}'?\n\n"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.controller.delete_requirement(req_id)

            if success:
                QMessageBox.information(self, "Success", message)
                self.refresh_table()
            else:
                QMessageBox.critical(self, "Error", message)

    def _on_search(self, query: str):
        """Handle search text change"""
        if not query.strip():
            self.refresh_table()
            return

        requirements = self.controller.search_requirements(query)
        self._populate_table(requirements)
