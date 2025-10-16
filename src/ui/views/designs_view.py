from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QSplitter, QGroupBox
)
from PyQt6.QtCore import Qt
from controllers.design_controller import DesignController
from ui.dialogs.design_dialog import DesignDialog
from ui.widgets.markdown_viewer import MarkdownViewer


class DesignsView(QWidget):
    """View for managing designs"""

    def __init__(self, controller: DesignController, requirement_controller):
        super().__init__()
        self.controller = controller
        self.requirement_controller = requirement_controller
        self.init_ui()
        self.load_designs()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Create splitter for table and preview
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setChildrenCollapsible(False)

        # Top section: Table
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(5)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(5)

        self.add_button = QPushButton("Add Design")
        self.add_button.clicked.connect(self.add_design)
        toolbar.addWidget(self.add_button)

        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_design)
        self.edit_button.setEnabled(False)
        toolbar.addWidget(self.edit_button)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_design)
        self.delete_button.setEnabled(False)
        toolbar.addWidget(self.delete_button)

        toolbar.addStretch()
        table_layout.addLayout(toolbar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Type", "Status", "Requirements", "Updated"
        ])

        # Configure column resize modes for responsiveness
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )  # ID
        header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )  # Name
        header.setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )  # Type
        header.setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )  # Status
        header.setSectionResizeMode(
            4, QHeaderView.ResizeMode.ResizeToContents
        )  # Requirements
        header.setSectionResizeMode(
            5, QHeaderView.ResizeMode.ResizeToContents
        )  # Updated

        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.doubleClicked.connect(self.edit_design)
        table_layout.addWidget(self.table)

        splitter.addWidget(table_widget)

        # Bottom section: Preview
        preview_group = QGroupBox("Description Preview")
        preview_layout = QVBoxLayout(preview_group)
        preview_layout.setContentsMargins(5, 5, 5, 5)

        self.preview = MarkdownViewer()
        preview_layout.addWidget(self.preview)

        splitter.addWidget(preview_group)

        # Set initial splitter sizes (60% table, 40% preview)
        splitter.setStretchFactor(0, 6)
        splitter.setStretchFactor(1, 4)

        layout.addWidget(splitter)

        # Store splitter for potential resize handling
        self.splitter = splitter

    def load_designs(self):
        """Load designs into the table"""
        designs = self.controller.get_all_designs()
        self.table.setRowCount(len(designs))

        for row, design in enumerate(designs):
            # ID
            id_item = QTableWidgetItem(str(design.id))
            id_item.setData(Qt.ItemDataRole.UserRole, design)
            self.table.setItem(row, 0, id_item)

            # Name
            self.table.setItem(row, 1, QTableWidgetItem(design.name))

            # Type
            self.table.setItem(row, 2, QTableWidgetItem(design.type))

            # Status
            self.table.setItem(row, 3, QTableWidgetItem(design.status))

            # Requirements count
            req_count = len(design.requirement_ids)
            self.table.setItem(row, 4, QTableWidgetItem(str(req_count)))

            # Updated date
            updated = design.updated_at.strftime("%Y-%m-%d %H:%M")
            self.table.setItem(row, 5, QTableWidgetItem(updated))

        # Update preview for selected item
        self.update_preview()

    def on_selection_changed(self):
        """Handle selection change"""
        has_selection = len(self.table.selectedItems()) > 0
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        self.update_preview()

    def update_preview(self):
        """Update the preview pane with selected design description"""
        design = self.get_selected_design()
        if design:
            self.preview.set_markdown(design.description)
        else:
            self.preview.set_markdown("*Select a design to view details*")

    def get_selected_design(self):
        """Get the currently selected design"""
        selection_model = self.table.selectionModel()
        if not selection_model:
            return None
        selected_rows = selection_model.selectedRows()
        if not selected_rows:
            return None
        row = selected_rows[0].row()
        item = self.table.item(row, 0)
        if not item:
            return None
        return item.data(Qt.ItemDataRole.UserRole)

    def add_design(self):
        """Add a new design"""
        # Get available requirements
        requirements = self.requirement_controller.get_all_requirements()

        dialog = DesignDialog(self, requirements=requirements)
        if dialog.exec():
            data = dialog.get_data()
            try:
                self.controller.create_design(
                    name=data['name'],
                    description=data['description'],
                    type=data['type'],
                    status=data['status'],
                    requirement_ids=data.get('requirement_ids', [])
                )
                self.load_designs()
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to create design: {str(e)}"
                )

    def edit_design(self):
        """Edit the selected design"""
        design = self.get_selected_design()
        if not design:
            return

        # Get available requirements
        requirements = self.requirement_controller.get_all_requirements()

        dialog = DesignDialog(self, design=design, requirements=requirements)
        if dialog.exec():
            data = dialog.get_data()
            try:
                design.name = data['name']
                design.description = data['description']
                design.type = data['type']
                design.status = data['status']
                design.requirement_ids = data.get('requirement_ids', [])
                self.controller.update_design(design)
                self.load_designs()
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to update design: {str(e)}"
                )

    def delete_design(self):
        """Delete the selected design"""
        design = self.get_selected_design()
        if not design:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete design '{design.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.controller.delete_design(design.id)
                self.load_designs()
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to delete design: {str(e)}"
                )
