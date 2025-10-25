import logging

from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QFileDialog, QWidget
from PySide6.QtCore import Slot

from shutterbug.gui.sidebar import Sidebar
from shutterbug.gui.viewer import Viewer
from shutterbug.gui.project import ShutterbugProject

from astropy.io import fits


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("Shutterbug")
        self.setGeometry(100, 100, 1200, 800)

        # Set up save/load functionality
        self.project = ShutterbugProject()

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

        # Set up image properties signals to slots
        self.sidebar.settings.image_properties.brightness_slider.valueChanged.connect(
            self.viewer.set_brightness
        )
        self.sidebar.settings.image_properties.contrast_slider.valueChanged.connect(
            self.viewer.set_contrast
        )

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

        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")
        undo_action = edit_menu.addAction("Undo")
        redo_action = edit_menu.addAction("Redo")

        # Help menu
        help_menu = menu_bar.addMenu("Help")
        about_action = help_menu.addAction("About Shutterbug")

        logging.debug("Menu bar set up")

    @Slot(str)
    def on_file_selected(self, filepath: str):
        """Called when a file is selected in the outliner"""
        logging.debug(f"File selected in outliner: {filepath}")
        # Load data if not already loaded
        if filepath not in self.fits_data:
            self.fits_data[filepath] = self.load_fits_image(filepath)

        # Tell viewer to display the image
        self.selected_file = filepath
        self.viewer.display_image(self.fits_data[filepath])

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
            self.add_fits_to_project(filename)

        if filenames:
            self.viewer.display_image(self.fits_data[filenames[0]])

    def add_fits_to_project(self, filename: str):
            # Add to outliner
            self.sidebar.outliner.add_item(filename)

            # Load and display in viewer
            self.fits_data[filename] = self.load_fits_image(filename)

    def load_fits_image(self, filepath: str):
        """Load FITS image from given filepath"""
        # This method can be implemented to load FITS data
        logging.debug(f"Loading FITS image from {filepath}")

        with fits.open(filepath) as hdul:
            data = hdul[0].data  #type: ignore
            # Assuming image data is in the primary HDU
            return data
    
    @Slot()
    def save_project(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Project", "", "Shutterbug Project (*.sbug)"
        )
        if filename:
            ShutterbugProject.save(filename, self.get_state())

    @Slot()
    def load_project(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "Shutterbug Project (*.sbug)"
        )
        if filename:
            ShutterbugProject.load(filename, self)

    def get_state(self):
        return {
            "outliner": self.sidebar.outliner.get_state(),
            "settings": self.sidebar.settings.get_state()
        }

    def set_state(self, state):
        print(state.keys())
        self.sidebar.outliner.set_state(state["outliner"])
        self.sidebar.settings.set_state(state["settings"])
            

    
