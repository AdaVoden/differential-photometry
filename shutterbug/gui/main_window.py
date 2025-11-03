import logging

import matplotlib.pyplot as plt

from PySide6.QtWidgets import (
    QMainWindow,
    QHBoxLayout,
    QFileDialog,
    QWidget,
    QProgressBar,
    QLabel,
)
from PySide6.QtCore import Slot, QCoreApplication, QPoint, Qt, Signal
from PySide6.QtGui import QMouseEvent, QUndoStack

from shutterbug.gui.sidebar import Sidebar
from shutterbug.gui.viewer import Viewer
from shutterbug.gui.project import ShutterbugProject
from shutterbug.gui.image_data import FITSImage, SelectedStar
from shutterbug.gui.progress_bar_handler import ProgressHandler
from shutterbug.gui.commands.image_commands import (
    SetBrightnessCommand,
    SetContrastCommand
)
from shutterbug.gui.commands.main_commands import (
    LoadImagesCommand,
    RemoveImagesCommand,
    FileSelectedCommand,
)

from pathlib import Path

from typing import List, Dict

import numpy as np


class MainWindow(QMainWindow):

    NEARNESS_TOLERANCE_DEFAULT = 20  # pixels

    star_selected = Signal(SelectedStar)

    def __init__(self):
        super().__init__()
        self.setObjectName("mainWindow")
        # Set window properties
        self.setWindowTitle("Shutterbug")
        self.setGeometry(100, 100, 1200, 800)

        self.fits_data: Dict[str, FITSImage] = {}  # Loaded FITS images
        # filename -> FITSImage

        # Set up undo stack
        self._undo_stack = QUndoStack()

        # Set up save/load functionality
        self.project = ShutterbugProject()

        # Create sidebar and viewer
        self.sidebar = Sidebar(self._undo_stack)
        self.viewer = Viewer(self._undo_stack)

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

        # Connect outliner signals
        self.sidebar.outliner.item_selected.connect(self.on_file_selected)
        self.sidebar.outliner.remove_item_requested.connect(
            self.on_remove_file_requested
        )

        # Set up image properties signals to slots
        self.sidebar.settings.image_properties.brightness_change_requested.connect(
            self.on_brightness_change_requested
        )
        self.sidebar.settings.image_properties.contrast_change_requested.connect(
            self.on_contrast_change_requested
        )

        # Handle Viewer signals
        self.viewer.clicked.connect(self.on_viewer_clicked)
        self.viewer.find_stars_requested.connect(self.find_stars_in_image)
        self.viewer.photometry_requested.connect(self.calculate_aperture_photometry)
        self.viewer.propagation_requested.connect(self.propagate_star_selection)
        self.viewer.batch_requested.connect(self.process_all_images)

        # Handle star selection signals
        self.star_selected.connect(self.sidebar.settings.show_star_properties)

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
        help_menu = menu_bar.addMenu("Help")
        about_action = help_menu.addAction("About Shutterbug")

        logging.debug("Menu bar set up")

    @Slot()
    def on_redo(self):
        if self._undo_stack.canRedo():
            self._undo_stack.redo()

    def on_undo(self):
        if self._undo_stack.canUndo():
            self._undo_stack.undo()

    @Slot(str)
    def on_file_selected(self, filename: str):
        """Called when a file is selected in the outliner"""
        logging.debug(f"File selected in outliner: {filename}")

        # Tell viewer to display the image
        self.selected_file = filename
        image = self.fits_data[filename]
        self.viewer.display_image(image)
        # Update image settings with image's information
        self.sidebar.settings.image_properties.set_brightness(image.brightness_offset)
        self.sidebar.settings.image_properties.set_contrast(image.contrast_factor)

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

        load_command = LoadImagesCommand(
            filenames,
            self,
            self.viewer,
            self.sidebar.outliner,
        )
        self._undo_stack.push(load_command)

    @Slot(str)
    def on_remove_file_requested(self, item_name: str):
        """Remove image from current project"""
        remove_command = RemoveImagesCommand(
            [item_name], self, self.viewer, self.sidebar.outliner
        )
        self._undo_stack.push(remove_command)

    @Slot(int)
    def on_brightness_change_requested(self, new_value: int):
        command = SetBrightnessCommand(self.sidebar.settings.image_properties,
                                       self.viewer,
                                       new_value
                                       )
        self._undo_stack.push(command)

    @Slot(int)
    def on_contrast_change_requested(self, new_value: int):
        command = SetContrastCommand(self.sidebar.settings.image_properties,
                                       self.viewer,
                                       new_value
                                       )
        self._undo_stack.push(command)

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

    @Slot(QMouseEvent)
    def on_viewer_clicked(self, event: QMouseEvent):
        """Handler for a click in the viewer"""
        if self.viewer.current_image is None:
            # No image, we don't care
            return

        # Alt + Click, remove a star
        if event.modifiers() == Qt.KeyboardModifier.AltModifier:
            if event.button() == Qt.MouseButton.LeftButton:
                self.remove_star_at_position(event.pos())
            return

        # if CTRL is held, add a reference star
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.button() == Qt.MouseButton.LeftButton:
                self.add_reference_star(event.pos())
            return

        if event.button() == Qt.MouseButton.LeftButton:
            self.select_target_star(event.pos())
            return

    @Slot()
    def calculate_aperture_photometry(self):
        current_image = self.viewer.current_image
        if current_image is None:
            return
        if current_image.stars is None:
            return
        if current_image.target_star_idx is None:
            return

        star = current_image.measure_magnitude_at_idx(current_image.target_star_idx)

        self.star_selected.emit(star)

    @Slot()
    def find_stars_in_image(self):
        current_image = self.viewer.current_image
        if current_image is None:
            return

        with self.progress_handler("Finding stars..."):
            current_image.find_stars()

    def select_target_star(self, coordinates: QPoint):
        """Creates a marker on image at coordinates"""
        current_image = self.viewer.current_image

        if current_image is None:
            return

        x, y = self.viewer.convert_to_image_coordinates(coordinates)

        star, idx = current_image.select_star_at_position(x, y)
        # Star not found
        if star is None or idx is None:
            return
        if idx in current_image.reference_star_idxs:
            # Target star cannot be a reference to itself
            return
        # Add new marker, replace old target if present
        if current_image.target_star_idx:
            old_target = current_image.get_star(current_image.target_star_idx)
            if old_target:
                self.viewer.remove_star_marker(old_target.x, old_target.y)

        self.viewer.add_star_marker(star.x, star.y, colour="cyan")

        current_image.target_star_idx = int(idx)

        self.star_selected.emit(star)

    def remove_star_at_position(self, coordinates: QPoint):
        """Removes a star at selected point"""
        img = self.viewer.current_image

        x, y = self.viewer.convert_to_image_coordinates(coordinates)

        if img is None:
            return  # No work required

        # Are we clicking near a target star?
        if img.target_star_idx is not None:
            target = img.get_star(img.target_star_idx)
            if target and self.is_near(x, y, target.x, target.y):
                img.target_star_idx = None
                self.viewer.remove_star_marker(target.x, target.y)
                return

        # Are we clicking near a reference star?
        for idx in img.reference_star_idxs[:]:  # make a copy
            ref = img.get_star(idx)
            if ref and self.is_near(x, y, ref.x, ref.y):
                img.reference_star_idxs.remove(idx)
                self.viewer.remove_star_marker(ref.x, ref.y)
                return

    def is_near(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        tolerance=NEARNESS_TOLERANCE_DEFAULT,
    ):
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5 <= tolerance

    def add_reference_star(self, coordinates: QPoint):
        """Select star at point as a reference star for calculations"""

        current_image = self.viewer.current_image

        if current_image is None:
            return

        x, y = self.viewer.convert_to_image_coordinates(coordinates)

        star, idx = current_image.select_star_at_position(x, y)
        # Star not found
        if star is None or idx is None:
            return

        if current_image.target_star_idx is not None:
            if current_image.target_star_idx == idx:
                # We cannot mark a target star as a reference to itself
                return
        self.viewer.add_star_marker(star.x, star.y, colour="magenta")

        current_image.reference_star_idxs.append(int(idx))

    @Slot()
    def process_all_images(self):
        """Generate light curve from all loaded images"""
        # Validate that there's data to work on
        if not self.fits_data:
            logging.error(f"No images available to work on")
            return  # No images to work on

        target_image = self.viewer.current_image

        if target_image is None:
            logging.error(f"No image currently loaded, aborting process")
            return  # No primary image to propagate from

        if target_image.target_star_idx is None:
            logging.error(
                f"Image {target_image.filename} has no target star, aborting process"
            )
            return  # We need a target star

        if target_image.reference_star_idxs is None:
            logging.error(
                f"Image {target_image.filename} has no reference stars, aborting process"
            )
            return  # We need reference stars to do math with

        # Unify star selections
        self.propagate_star_selection(target_image)

        with self.progress_handler("Processing images..."):
            results = []
            for img in self.fits_data.values():
                if img.target_star_idx is None:
                    logging.error(
                        f"Image {img.filename} did not successfully propagate stars, skipping"
                    )
                    continue  # Did not propagate, do not use

                # No repetition if it's in one list
                idxs = [img.target_star_idx]
                idxs.extend(img.reference_star_idxs)

                stars = []
                for idx in idxs:
                    # Need magnitude for diff mag
                    star = img.measure_magnitude_at_idx(
                        idx=idx,
                        aperture_radius=img.APERTURE_RADIUS_DEFAULT,
                        annulus_inner=img.ANNULUS_INNER_DEFAULT,
                        annulus_outer=img.ANNULUS_OUTER_DEFAULT,
                    )
                    if star:
                        stars.append(star)
                    else:
                        logging.error(
                            f"Failed to measure star magnitude in image {img.filename}, index {idx}, skipping"
                        )
                        break
                # Cannot continue without sufficient number of stars
                if len(stars) != len(idxs):
                    logging.error(
                        f"Failed to measure sufficient stars in image {img.filename}, skipping image"
                    )
                    continue

                result = self.calculate_differential_magnitude(
                    target_star=stars[0], ref_stars=stars[1:]
                )
                results.append(
                    {
                        "filename": img.filename,
                        "time": img.observation_time,
                        "magnitude": result,
                        "n_references": len(stars[1:]),
                    }
                )

            self.generate_light_curve(results)

    def process_single_image(self, image: FITSImage):
        """Process one image for differential photometry"""
        pass

    @Slot(FITSImage)
    def propagate_star_selection(self, image: FITSImage):
        """Propagates star selection across all images"""
        if not image.target_star_idx and not image.reference_star_idxs:
            logging.error(f"No markers in image {image.filename} to propagate")
            return  # No markers to propagate, no work to do

        for img in self.fits_data.values():
            with self.progress_handler("Propagating stars..."):
                if img == image:
                    # Don't propagate to self
                    continue

                if img.stars is None:
                    img.find_stars()

                # Clear existing selections before propagation
                img.target_star_idx = None
                img.reference_star_idxs = []

                # Propagate target
                if image.target_star_idx:
                    star = image.get_star(image.target_star_idx)
                    if star:
                        _, t_s_idx = img.find_nearest_star(
                            star.x, star.y, FITSImage.MAX_DISTANCE_DEFAULT
                        )
                        if t_s_idx:
                            img.target_star_idx = int(t_s_idx)

                # Propagate references
                for idx in image.reference_star_idxs:
                    star = image.get_star(idx)
                    if star:
                        _, ref_idx = img.find_nearest_star(
                            star.x, star.y, FITSImage.MAX_DISTANCE_DEFAULT
                        )
                        if ref_idx:
                            img.reference_star_idxs.append(int(ref_idx))

    def calculate_differential_magnitude(
        self, target_star: SelectedStar, ref_stars: List[SelectedStar]
    ):
        """Calculate differential magnitude on target image and stars"""
        ref_mags = [ref.magnitude for ref in ref_stars]
        ref_mags = np.asarray(ref_mags)

        # - ref_mags + target_mag == target_mag - ref_mags
        return np.mean((-1 * ref_mags) + target_star.magnitude)

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
