import logging

from PySide6.QtCore import QCoreApplication, Slot
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProgressBar,
    QWidget,
)
from shutterbug.core.app_controller import AppController


from .commands import LoadImagesCommand
from .project import ShutterbugProject
from .sidebar import Sidebar
from .views import MultiViewer


class MainWindow(QMainWindow):

    def __init__(self, controller: AppController):
        super().__init__()
        self.setObjectName("mainWindow")
        # Set window properties
        self.setWindowTitle("Shutterbug")
        self.setGeometry(100, 100, 1200, 800)

        # Managers
        self.image_manager = controller.images
        self.star_catalog = controller.stars
        self.graph_manager = controller.graphs

        self.controller = controller
        # Set up save/load functionality
        self.project = ShutterbugProject()

        # Create sidebar and viewer
        self.sidebar = Sidebar(controller)
        self.viewer = MultiViewer(controller)

        # Set up central widget with horizontal layout
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout()
        central.setLayout(main_layout)

        # Remove styling from layouts
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(2)

        # Add in contents
        main_layout.addWidget(self.viewer, stretch=3)  # Viewer takes most space
        main_layout.addWidget(self.sidebar, stretch=1)  # Sidebar on the right

        # Set up menu bar
        self.setup_menu_bar()

        # Set up status bar
        self.status_bar = self.statusBar()
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

        # Set up progress bar (Hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(100)  # Pixels
        self.progress_bar.setVisible(False)
        # Handler for context handling

        # Add to status bar
        self.status_bar.addPermanentWidget(self.progress_bar)

        logging.debug("Main window initialized")

    def setup_menu_bar(self):
        """Set up the menu bar with File, Edit, View, and Help menus"""
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")

        open_action = file_menu.addAction("Open Image")
        open_action.triggered.connect(self.open_fits)

        load_action = file_menu.addAction("Load Project")
        load_action.triggered.connect(self.load_project)

        save_action = file_menu.addAction("Save Project")
        save_action.triggered.connect(self.save_project)

        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.exit)

        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")
        undo_action = edit_menu.addAction("Undo")
        undo_action.triggered.connect(self.controller.on_undo)

        redo_action = edit_menu.addAction("Redo")
        redo_action.triggered.connect(self.controller.on_redo)

        diff_menu = edit_menu.addMenu("Differential")

        image_action = diff_menu.addAction("Differential Photometry (image)")
        image_action.triggered.connect(self.controller.differential_image)

        all_action = diff_menu.addAction("Differential Photometry (all)")
        all_action.triggered.connect(self.controller.differential_all)

        graph_action = diff_menu.addAction("Graph selected star")
        graph_action.triggered.connect(self.controller.create_graph_from_selection)

        # Help menu
        # help_menu = menu_bar.addMenu("Help")
        # about_action = help_menu.addAction("About Shutterbug")

        logging.debug("Menu bar set up")

    @Slot()
    def open_fits(self):
        """Open a FITS image file and load it into the viewer"""
        logging.debug("Opening FITS file dialog")
        filenames, _ = QFileDialog.getOpenFileNames(
            self,
            "Open FITS Image",
            "",
            "FITS Files (*.fits *.fit *.fts);;All Files (*)",
        )

        load_command = LoadImagesCommand(filenames, self.controller)
        self.controller._undo_stack.push(load_command)

    @Slot()
    def save_project(self):
        return
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Project", "", "Shutterbug Project (*.sbug)"
        )
        if filename:
            ShutterbugProject.save(filename, self.get_state())

    @Slot()
    def load_project(self):
        return
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "Shutterbug Project (*.sbug)"
        )
        if filename:
            ShutterbugProject.load(filename, self)

    @Slot()
    def exit(self):
        QCoreApplication.quit()
