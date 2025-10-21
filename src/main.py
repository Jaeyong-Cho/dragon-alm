import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget
from repositories.sqlite_repository import SQLiteRequirementRepository
from repositories.sqlite_design_repository import SQLiteDesignRepository
from managers.requirement_manager import RequirementManager
from managers.design_manager import DesignManager
from controllers.requirement_controller import RequirementController
from controllers.design_controller import DesignController
from ui.views.requirements_view import RequirementsView
from ui.views.designs_view import DesignsView
from ui.views.toolbar import ToolBar


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dragon ALM")
        self.setMinimumSize(1200, 800)

        # Initialize components
        db_path = "dragon_alm.db"

        # Requirements
        req_repository = SQLiteRequirementRepository(db_path)
        req_manager = RequirementManager(req_repository)
        req_controller = RequirementController(req_manager)

        # Design
        design_repository = SQLiteDesignRepository(db_path)
        design_manager = DesignManager(design_repository)
        design_controller = DesignController(design_manager)
        
        # Create Toolbar
        toolbar = ToolBar(self)
        
        self.addToolBar(toolbar)

        # Create tab widget
        tabs = QTabWidget()

        # Create views
        requirements_view = RequirementsView(req_controller, design_controller)
        tabs.addTab(requirements_view, "Requirements")

        designs_view = DesignsView(design_controller, req_controller)
        tabs.addTab(designs_view, "Design")

        # Add placeholder tabs
        tabs.addTab(QTabWidget(), "Implementation")
        tabs.addTab(QTabWidget(), "Traceability")

        self.setCentralWidget(tabs)

def main():
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
