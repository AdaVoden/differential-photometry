from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QFileDialog, QWidget
from PySide6.QtCore import Slot

from shutterbug.gui.sidebar import Sidebar
from shutterbug.gui.viewer import Viewer


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("Shutterbug")
        self.setGeometry(100, 100, 1200, 800)

        # Create sidebar and viewer
        self.sidebar = Sidebar()
        self.viewer = Viewer()

        # Set up central widget with horizontal layout
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout()
        central.setLayout(main_layout)

        # Add in contents
        main_layout.addWidget(self.viewer, stretch=3)  # Viewer takes most space
        main_layout.addWidget(self.sidebar, stretch=1)  # Sidebar on the right

        # Set up menu bar
        self.setup_menu_bar()

    def setup_menu_bar(self):
        """Set up the menu bar with File, Edit, View, and Help menus"""
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")
        open_action = file_menu.addAction("Open Image")
        open_action.triggered.connect(self.open_fits)

        save_action = file_menu.addAction("Save Project")
        exit_action = file_menu.addAction("Exit")

        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")
        undo_action = edit_menu.addAction("Undo")
        redo_action = edit_menu.addAction("Redo")

        # View menu
        view_menu = menu_bar.addMenu("View")
        toggle_sidebar_action = view_menu.addAction("Toggle Sidebar")

        # Help menu
        help_menu = menu_bar.addMenu("Help")
        about_action = help_menu.addAction("About Shutterbug")

    @Slot()
    def open_fits(self):
        """Open a FITS image file and load it into the viewer"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open FITS Image",
            "",
            "FITS Files (*.fits *.fit *.fts);;All Files (*)",
        )
        if filename:
            self.viewer.load_fits_image(filename)
