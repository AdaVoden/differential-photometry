import logging

from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QFileDialog, QWidget
from PySide6.QtCore import Slot, QCoreApplication

from shutterbug.gui.sidebar import Sidebar
from shutterbug.gui.viewer import Viewer
from shutterbug.gui.project import ShutterbugProject
from shutterbug.gui.image_data import FITSImage

from astropy.io import fits

from pathlib import Path


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

        self.fits_data = {}  # Loaded FITS images
        # filename -> FITSImage

        # Connect outliner selection signal
        self.sidebar.outliner.item_selected.connect(self.on_file_selected)

        # Set up image properties signals to slots
        self.sidebar.settings.image_properties.brightness_slider.valueChanged.connect(
            self.viewer.set_brightness
        )
        self.sidebar.settings.image_properties.contrast_slider.valueChanged.connect(
            self.viewer.set_contrast
        )

        # Set up star being selected to Settings
        self.viewer.star_selected.connect(self.sidebar.settings.show_star_properties)

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
        redo_action = edit_menu.addAction("Redo")

        # Help menu
        help_menu = menu_bar.addMenu("Help")
        about_action = help_menu.addAction("About Shutterbug")

        logging.debug("Menu bar set up")

    @Slot(str)
    def on_file_selected(self, filename: str):
        """Called when a file is selected in the outliner"""
        logging.debug(f"File selected in outliner: {filename}")

        # Tell viewer to display the image
        self.selected_file = filename
        self.viewer.display_image(self.fits_data[filename])

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
            image = FITSImage(filename, self.load_fits_image(filename))
            self.add_fits_to_project(image)

        if filenames:
            filepath = Path(filenames[0])
            self.viewer.display_image(self.fits_data[filepath.name + filepath.suffix])

    def add_fits_to_project(self, image: FITSImage):
        # Add to outliner
        self.sidebar.outliner.add_item(image.filename)

        # Load and display in viewer
        self.fits_data[image.filename] = image

    def load_fits_image(self, filepath: str):
        """Load FITS image from given filepath"""
        # This method can be implemented to load FITS data
        logging.debug(f"Loading FITS image from {filepath}")

        with fits.open(filepath) as hdul:
            data = hdul[0].data  # type: ignore
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

    @Slot()
    def exit(self):
        QCoreApplication.quit()

    def get_state(self):
        return {
            "outliner": self.sidebar.outliner.get_state(),
            "settings": self.sidebar.settings.get_state(),
        }

    def set_state(self, state):
        self.sidebar.outliner.set_state(state["outliner"])
        self.sidebar.settings.set_state(state["settings"])
