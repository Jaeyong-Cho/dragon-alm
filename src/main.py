import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget
from repositories.sqlite_repository import SQLiteRequirementRepository
from managers.requirement_manager import RequirementManager
from controllers.requirement_controller import RequirementController
from ui.views.requirements_view import RequirementsView

class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dragon ALM")
        self.setMinimumSize(1200, 800)

        # Initialize components
        db_path = "dragon_alm.db"
        repository = SQLiteRequirementRepository(db_path)
        manager = RequirementManager(repository)
        controller = RequirementController(manager)

        # Create tab widget
        tabs = QTabWidget()

        # Create requirements view
        requirements_view = RequirementsView(controller)
        tabs.addTab(requirements_view, "Requirements")

        # Add placeholder tabs
        tabs.addTab(QTabWidget(), "Design")
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
