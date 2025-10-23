from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QMessageBox, QLineEdit, QLabel, QListWidget, QListWidgetItem,
    QTextBrowser, QScrollArea, QFormLayout, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import List, Optional
from controllers.requirement_controller import RequirementController
from controllers.design_controller import DesignController
from models.requirement import Requirement
from ui.dialogs.requirement_dialog import RequirementDialog
import markdown


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

    def _init_toolbar(self):
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

        return toolbar

    def _init_navigator(self):
        """Initialize the navigator list"""
        navigator_layout = QVBoxLayout()
        
        # Navigator title
        nav_label = QLabel("Requirements")
        nav_label.setStyleSheet("font-weight: bold; padding: 5px;")
        navigator_layout.addWidget(nav_label)
        
        # List widget for requirements
        self.navigator_list = QListWidget()
        self.navigator_list.setAlternatingRowColors(True)
        self.navigator_list.itemSelectionChanged.connect(self._on_navigator_selection_changed)
        self.navigator_list.itemDoubleClicked.connect(self._on_edit)
        navigator_layout.addWidget(self.navigator_list)
        
        self.navigator = QWidget()
        self.navigator.setLayout(navigator_layout)

    def _init_property_view(self):
        """Initialize the property view"""
        property_layout = QVBoxLayout()
        
        # Property title
        property_label = QLabel("Properties")
        property_label.setStyleSheet("font-weight: bold; padding: 5px;")
        property_layout.addWidget(property_label)
        
        # Scroll area for properties
        property_scroll = QScrollArea()
        property_scroll.setWidgetResizable(True)
        property_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Container for property content
        self.property_container = QWidget()
        self.property_container_layout = QVBoxLayout(self.property_container)
        self.property_container_layout.setSpacing(10)
        
        # Basic Information Group
        self.basic_info_group = QGroupBox("Basic Information")
        self.basic_info_layout = QFormLayout()
        self.basic_info_group.setLayout(self.basic_info_layout)
        
        self.prop_id_label = QLabel("-")
        self.prop_title_label = QLabel("-")
        self.prop_category_label = QLabel("-")
        
        self.basic_info_layout.addRow("ID:", self.prop_id_label)
        self.basic_info_layout.addRow("Title:", self.prop_title_label)
        self.basic_info_layout.addRow("Category:", self.prop_category_label)
        
        self.property_container_layout.addWidget(self.basic_info_group)
        
        # Status Group
        self.status_group = QGroupBox("Status")
        self.status_layout = QFormLayout()
        self.status_group.setLayout(self.status_layout)
        
        self.prop_status_label = QLabel("-")
        self.prop_priority_label = QLabel("-")
        
        self.status_layout.addRow("Status:", self.prop_status_label)
        self.status_layout.addRow("Priority:", self.prop_priority_label)
        
        self.property_container_layout.addWidget(self.status_group)
        
        # Timestamps Group
        self.timestamps_group = QGroupBox("Timestamps")
        self.timestamps_layout = QFormLayout()
        self.timestamps_group.setLayout(self.timestamps_layout)
        
        self.prop_created_label = QLabel("-")
        self.prop_updated_label = QLabel("-")
        
        self.timestamps_layout.addRow("Created:", self.prop_created_label)
        self.timestamps_layout.addRow("Updated:", self.prop_updated_label)
        
        self.property_container_layout.addWidget(self.timestamps_group)
        
        # Links Group
        self.links_group = QGroupBox("Links")
        self.links_layout = QVBoxLayout()
        self.links_group.setLayout(self.links_layout)
        
        self.prop_designs_label = QLabel("-")
        self.prop_designs_label.setWordWrap(True)
        self.links_layout.addWidget(QLabel("<strong>Linked Designs:</strong>"))
        self.links_layout.addWidget(self.prop_designs_label)
        
        self.prop_tests_label = QLabel("-")
        self.prop_tests_label.setWordWrap(True)
        self.links_layout.addWidget(QLabel("<strong>Linked Tests:</strong>"))
        self.links_layout.addWidget(self.prop_tests_label)
        
        self.property_container_layout.addWidget(self.links_group)
        
        # Add stretch at the end
        self.property_container_layout.addStretch()
        
        property_scroll.setWidget(self.property_container)
        property_layout.addWidget(property_scroll)
        
        self.property_view = QWidget()
        self.property_view.setLayout(property_layout)
        
        # Initially hide properties
        self._clear_property_view()

    def _init_contents_view(self):
        """Initialize the contents view with Markdown rendering"""
        contents_layout = QVBoxLayout()
        
        # Contents title
        contents_label = QLabel("Description")
        contents_label.setStyleSheet("font-weight: bold; padding: 5px;")
        contents_layout.addWidget(contents_label)
        
        # Scroll area for multiple requirements
        self.contents_scroll = QScrollArea()
        self.contents_scroll.setWidgetResizable(True)
        self.contents_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.contents_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Container widget for all requirement descriptions
        self.contents_container = QWidget()
        self.contents_container_layout = QVBoxLayout(self.contents_container)
        self.contents_container_layout.setSpacing(20)
        self.contents_container_layout.addStretch()
        
        self.contents_scroll.setWidget(self.contents_container)
        contents_layout.addWidget(self.contents_scroll)
        
        self.contents_view = QWidget()
        self.contents_view.setLayout(contents_layout)
        
        # Dictionary to store text browsers by requirement ID
        self.content_browsers = {}

    def _init_main_view(self):
        self.main_view = QHBoxLayout()

        self._init_navigator()
        self._init_contents_view()
        self._init_property_view()

        self.main_view.addWidget(self.navigator, 1)
        self.main_view.addWidget(self.contents_view, 3)
        self.main_view.addWidget(self.property_view, 1)

    def _init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)

        toolbar = self._init_toolbar()
        layout.addLayout(toolbar)

        self._init_main_view()
        layout.addLayout(self.main_view)

        # Status bar
        self.status_label = QLabel("0 requirements")
        layout.addWidget(self.status_label)

    def refresh_table(self):
        """Refresh view with current requirements"""
        requirements = self.controller.get_all_requirements()
        self._populate_navigator(requirements)
        
        # Update status
        self.status_label.setText(
            f"{len(requirements)} requirement{'s' if len(requirements) != 1 else ''}"
        )

    def _populate_navigator(self, requirements: List[Requirement]):
        """Populate navigator with requirements"""
        self.navigator_list.clear()
        
        for req in requirements:
            item_text = f"{req.id}: {req.title}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, req.id)
            self.navigator_list.addItem(item)
        
        # Populate contents view
        self._populate_contents(requirements)

    def _populate_contents(self, requirements: List[Requirement]):
        """Populate contents view with all requirement descriptions"""
        # Clear existing content browsers
        for browser in self.content_browsers.values():
            browser.deleteLater()
        self.content_browsers.clear()
        
        # Clear layout
        while self.contents_container_layout.count() > 1:  # Keep the stretch
            item = self.contents_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add requirement descriptions
        for req in requirements:
            # Create a container for each requirement
            req_widget = QWidget()
            req_widget.setObjectName(f"req_{req.id}")
            req_layout = QVBoxLayout(req_widget)
            req_layout.setContentsMargins(10, 10, 10, 10)
            
            # Requirement header
            header_label = QLabel(f"<h3>{req.id}: {req.title}</h3>")
            header_label.setTextFormat(Qt.TextFormat.RichText)
            req_layout.addWidget(header_label)
            
            # Metadata
            meta_text = f"<p><strong>Status:</strong> {req.status.value} | "
            meta_text += f"<strong>Priority:</strong> {req.priority.value} | "
            meta_text += f"<strong>Category:</strong> {req.category}</p>"
            meta_label = QLabel(meta_text)
            meta_label.setTextFormat(Qt.TextFormat.RichText)
            meta_label.setStyleSheet("color: #666; font-size: 10pt;")
            req_layout.addWidget(meta_label)
            
            # Description with Markdown rendering
            browser = QTextBrowser()
            browser.setOpenExternalLinks(True)
            browser.setMinimumHeight(150)
            
            # Convert Markdown to HTML
            if req.description:
                html_content = markdown.markdown(
                    req.description,
                    extensions=['extra', 'codehilite', 'fenced_code', 'tables']
                )
                browser.setHtml(f"<style>body {{ font-family: sans-serif; }}</style>{html_content}")
            else:
                browser.setHtml("<p><em>No description provided.</em></p>")
            
            req_layout.addWidget(browser)
            
            # Add separator
            separator = QLabel()
            separator.setStyleSheet("border-bottom: 1px solid #ccc; margin: 10px 0;")
            req_layout.addWidget(separator)
            
            # Insert before stretch
            self.contents_container_layout.insertWidget(
                self.contents_container_layout.count() - 1, 
                req_widget
            )
            
            # Store browser reference
            self.content_browsers[req.id] = req_widget

    def _update_property_view(self, req_id: str):
        """Update property view with selected requirement details"""
        requirement = self.controller.manager.get_requirement(req_id)
        
        if requirement is None:
            self._clear_property_view()
            return
        
        # Basic Information
        self.prop_id_label.setText(requirement.id)
        self.prop_title_label.setText(requirement.title)
        self.prop_title_label.setWordWrap(True)
        self.prop_category_label.setText(requirement.category)
        
        # Status
        self.prop_status_label.setText(requirement.status.value)
        self.prop_priority_label.setText(requirement.priority.value)
        
        # Apply color based on priority
        priority_colors = {
            "Critical": "#d32f2f",
            "High": "#f57c00",
            "Medium": "#fbc02d",
            "Low": "#388e3c"
        }
        priority_color = priority_colors.get(requirement.priority.value, "#000")
        self.prop_priority_label.setStyleSheet(f"color: {priority_color}; font-weight: bold;")
        
        # Timestamps
        self.prop_created_label.setText(requirement.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        self.prop_updated_label.setText(requirement.updated_at.strftime("%Y-%m-%d %H:%M:%S"))
        
        # Links
        # if requirement.linked_design_ids:
        #     designs_text = "<ul style='margin: 5px 0; padding-left: 20px;'>"
        #     for design_id in requirement.linked_design_ids:
        #         designs_text += f"<li>{design_id}</li>"
        #     designs_text += "</ul>"
        #     self.prop_designs_label.setText(designs_text)
        #     self.prop_designs_label.setTextFormat(Qt.TextFormat.RichText)
        # else:
        #     self.prop_designs_label.setText("<em>No linked designs</em>")
        #     self.prop_designs_label.setTextFormat(Qt.TextFormat.RichText)
        
        # if requirement.linked_test_ids:
        #     tests_text = "<ul style='margin: 5px 0; padding-left: 20px;'>"
        #     for test_id in requirement.linked_test_ids:
        #         tests_text += f"<li>{test_id}</li>"
        #     tests_text += "</ul>"
        #     self.prop_tests_label.setText(tests_text)
        #     self.prop_tests_label.setTextFormat(Qt.TextFormat.RichText)
        # else:
        #     self.prop_tests_label.setText("<em>No linked tests</em>")
        #     self.prop_tests_label.setTextFormat(Qt.TextFormat.RichText)

    def _clear_property_view(self):
        """Clear the property view"""
        self.prop_id_label.setText("-")
        self.prop_title_label.setText("-")
        self.prop_category_label.setText("-")
        self.prop_status_label.setText("-")
        self.prop_priority_label.setText("-")
        self.prop_priority_label.setStyleSheet("")
        self.prop_created_label.setText("-")
        self.prop_updated_label.setText("-")
        self.prop_designs_label.setText("-")
        self.prop_tests_label.setText("-")

    def _on_navigator_selection_changed(self):
        """Handle navigator selection change"""
        current_item = self.navigator_list.currentItem()
        if current_item:
            req_id = current_item.data(Qt.ItemDataRole.UserRole)
            self._scroll_to_requirement(req_id)
            self._update_property_view(req_id)
            self.edit_button.setEnabled(True)
            self.delete_button.setEnabled(True)
            self.requirement_selected.emit(req_id)
        else:
            self._clear_property_view()
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)

    def _scroll_to_requirement(self, req_id: str):
        """Scroll to the requirement in contents view"""
        if req_id in self.content_browsers:
            widget = self.content_browsers[req_id]
            self.contents_scroll.ensureWidgetVisible(widget)
            # Highlight the selected requirement temporarily
            widget.setStyleSheet("background-color: #e3f2fd; border-radius: 5px;")
            # Reset other highlights
            for other_id, other_widget in self.content_browsers.items():
                if other_id != req_id:
                    other_widget.setStyleSheet("")

    def _select_requirement_in_table(self, req_id: str):
        """Select requirement in table by ID"""
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).text() == req_id:
                self.table.selectRow(row)
                break

    def _on_selection_changed(self):
        """Handle selection change"""
        has_selection = len(self.table.selectedItems()) > 0
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

        if has_selection:
            req_id = self.table.item(self.table.currentRow(), 0).text()
            self._select_requirement_in_navigator(req_id)
            self._update_property_view(req_id)
            self.requirement_selected.emit(req_id)
        else:
            self._clear_property_view()

    def _select_requirement_in_navigator(self, req_id: str):
        """Select requirement in navigator by ID"""
        for i in range(self.navigator_list.count()):
            item = self.navigator_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == req_id:
                self.navigator_list.setCurrentItem(item)
                break

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
        current_item = self.navigator_list.currentItem()
        if not current_item:
            return

        req_id = current_item.data(Qt.ItemDataRole.UserRole)
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
        current_item = self.navigator_list.currentItem()
        if not current_item:
            return

        req_id = current_item.data(Qt.ItemDataRole.UserRole)
        requirement = self.controller.manager.get_requirement(req_id)
        
        if requirement is None:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete requirement '{req_id}: {requirement.title}'?\n\n"
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
        self._populate_navigator(requirements)
        
        # Update status
        self.status_label.setText(
            f"{len(requirements)} requirement{'s' if len(requirements) != 1 else ''}"
        )
