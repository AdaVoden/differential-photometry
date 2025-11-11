import logging
from typing import List

import matplotlib.pyplot as plt
import numpy as np
from PySide6.QtCore import QCoreApplication, Slot
from PySide6.QtGui import QUndoStack
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProgressBar,
    QWidget,
)
from shutterbug.core.models import FITSModel, StarMeasurement
from shutterbug.core.managers import ImageManager, StarCatalog
from shutterbug.core.progress_bar_handler import ProgressHandler
from .project import ShutterbugProject
from .sidebar import Sidebar
from .views import MultiViewer

from .commands import LoadImagesCommand


class MainWindow(QMainWindow):

    NEARNESS_TOLERANCE_DEFAULT = 20  # pixels

    def __init__(self):
        super().__init__()
        self.setObjectName("mainWindow")
        # Set window properties
        self.setWindowTitle("Shutterbug")
        self.setGeometry(100, 100, 1200, 800)

        self.image_manager = ImageManager()
        self.star_catalog = StarCatalog()

        # Set up undo stack
        self._undo_stack = QUndoStack()

        # Set up save/load functionality
        self.project = ShutterbugProject()

        # Create sidebar and viewer
        self.sidebar = Sidebar(self._undo_stack)
        self.viewer = MultiViewer(self._undo_stack)

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
        self.progress_handler = ProgressHandler(self.progress_bar, self.status_label)

        # Add to status bar
        self.status_bar.addPermanentWidget(self.progress_bar)

        # Handle Viewer signals
        self.viewer.propagation_requested.connect(self.propagate_star_selection)
        self.viewer.batch_requested.connect(self.process_all_images)

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
        undo_action.triggered.connect(self.on_undo)

        redo_action = edit_menu.addAction("Redo")
        redo_action.triggered.connect(self.on_redo)

        # Help menu
        # help_menu = menu_bar.addMenu("Help")
        # about_action = help_menu.addAction("About Shutterbug")

        logging.debug("Menu bar set up")

    @Slot()
    def on_redo(self):
        if self._undo_stack.canRedo():
            self._undo_stack.redo()

    @Slot()
    def on_undo(self):
        if self._undo_stack.canUndo():
            self._undo_stack.undo()

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

        load_command = LoadImagesCommand(filenames, self.image_manager)
        self._undo_stack.push(load_command)

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

    def is_near(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        tolerance=NEARNESS_TOLERANCE_DEFAULT,
    ):
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5 <= tolerance

    @Slot()
    def process_all_images(self):
        """Generate light curve from all loaded images"""
        current_image = self.image_manager.active_image

        if current_image is None:
            return  # No work required

        self.propagate_star_selection(current_image)
        for image in self.image_manager.get_all_images():
            self.process_single_image(image)

    def process_single_image(self, image: FITSModel):
        """Process one image for differential photometry"""

        for star in image.star_manager.get_all_stars():
            image.measure_star_magnitude(star)

    @Slot(FITSModel)
    def propagate_star_selection(self, image: FITSModel):
        """Propagates star selection across all images"""
        image_manager = self.image_manager
        stars = image.star_manager.get_all_stars()

        with self.progress_handler("Propagating stars..."):
            for img in image_manager.get_all_images():
                if img != image:
                    # Propagate to all other images, ignore target

                    for star in stars:
                        with self.progress_handler("Finding stars in image..."):
                            star_data, _ = img.find_nearest_star(star.x, star.y)

                        if star_data:
                            measurement = StarMeasurement(
                                x=star_data["xcentroid"],
                                y=star_data["ycentroid"],
                                time=img.observation_time,
                                image=img.filename,
                            )
                            img.star_manager.add_star(measurement)

    def calculate_differential_magnitude(
        self, target_star: StarMeasurement, ref_stars: List[StarMeasurement]
    ):
        """Calculate differential magnitude on target image and stars"""
        ref_mags = [ref.mag for ref in ref_stars]
        ref_mags = np.asarray(ref_mags)

        # - ref_mags + target_mag == target_mag - ref_mags
        return np.mean((-1 * ref_mags) + target_star.mag)

    def generate_light_curve(self, results):
        """Create light curve from data"""

        # sort by time, just in case
        results = sorted(results, key=lambda x: x["time"])

        times = [r["time"] for r in results]
        mags = [r["magnitude"] for r in results]

        plt.figure(figsize=(12, 6))
        plt.scatter(x=times, y=mags, marker="o")
        plt.xlabel("Time (JD)")
        plt.ylabel("Differential Magnitude")
        plt.title("Light Curve")
        plt.gca().invert_yaxis()  # Magnitude increases downward
        plt.grid(True, alpha=0.3)
        plt.show()  # Probably need to pipe it somewhere.
