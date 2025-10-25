import logging

from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QFileDialog, QWidget
from PySide6.QtCore import Slot

from shutterbug.gui.sidebar import Sidebar
from shutterbug.gui.viewer import Viewer

from astropy.io import fits


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

        self.fits_data = {}  # Dictionary to hold loaded FITS data
        # filepath -> data

        # Connect outliner selection signal
        self.sidebar.outliner.item_selected.connect(self.on_file_selected)

        logging.debug("Main window initialized")

    @Slot(str)
    def on_file_selected(self, filepath):
        """Called when a file is selected in the outliner"""
        logging.debug(f"File selected in outliner: {filepath}")
        # Load data if not already loaded
        if filepath not in self.fits_data:
            self.fits_data[filepath] = self.load_fits_image(filepath)

        # Tell viewer to display the image
        self.viewer.display_image(self.fits_data[filepath])

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

        for filename in filenames:
            # Add to outliner
            self.sidebar.outliner.add_item(filename)

            # Load and display in viewer
            self.fits_data[filename] = self.load_fits_image(filename)
        if filenames:
            self.viewer.display_image(self.fits_data[filenames[0]])

    def load_fits_image(self, filepath):
        """Load FITS image from given filepath"""
        # This method can be implemented to load FITS data
        logging.debug(f"Loading FITS image from {filepath}")

        with fits.open(filepath) as hdul:
            data = hdul[0].data  # Assuming image data is in the primary HDU
            return data
