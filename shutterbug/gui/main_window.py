import logging

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
from shutterbug.core.managers import (
    GraphManager,
    ImageManager,
    MeasurementManager,
    SelectionManager,
    StarCatalog,
)
from shutterbug.core.models import FITSModel, StarMeasurement
from shutterbug.core.progress_bar_handler import ProgressHandler
from shutterbug.core.utility.photometry import (
    calculate_differential_magnitude,
    measure_star_magnitude,
)

from .commands import LoadImagesCommand
from .project import ShutterbugProject
from .sidebar import Sidebar
from .views import MultiViewer


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setObjectName("mainWindow")
        # Set window properties
        self.setWindowTitle("Shutterbug")
        self.setGeometry(100, 100, 1200, 800)

        # Set up undo stack
        self._undo_stack = QUndoStack()

        # Instantiate singletons
        self.image_manager = ImageManager()
        self.star_catalog = StarCatalog()
        self.measure_manager = MeasurementManager()
        self.graph_manager = GraphManager()
        self.selection_manager = SelectionManager()

        # Set up save/load functionality
        self.project = ShutterbugProject()

        # Create sidebar and viewer
        self.sidebar = Sidebar(self._undo_stack)
        self.viewer = MultiViewer(self._undo_stack)
        self.outliner_model = self.sidebar.outliner.model

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

        # Handle Selection Signals
        self.selection_manager.image_selected.connect(
            self.image_manager.set_active_image
        )

        # Handle Viewer signals
        self.viewer.propagation_requested.connect(self.propagate_star_selection)
        self.viewer.batch_requested.connect(self.process_all_images)

        # Handle Outliner signals
        self.sidebar.object_selected.connect(self.selection_manager.set_selected_object)
        self.image_manager.image_added.connect(self.outliner_model.add_image)
        self.graph_manager.graph_added.connect(self.outliner_model.add_graph)
        self.star_catalog.star_added.connect(self.outliner_model.add_star)

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

        diff_menu = edit_menu.addMenu("Differential")

        image_action = diff_menu.addAction("Differential Photometry (image)")
        image_action.triggered.connect(self.differential_image)

        all_action = diff_menu.addAction("Differential Photometry (all)")
        all_action.triggered.connect(self.differential_all)

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

        for star in self.measure_manager.get_all_measurements(image.filename):
            measure_star_magnitude(star, data=image.data)

    @Slot(FITSModel)
    def propagate_star_selection(self, image: FITSModel):
        """Propagates star selection across all images"""
        image_manager = self.image_manager
        stars = self.measure_manager.get_all_measurements(image.filename)

        with self.progress_handler("Propagating stars..."):
            for img in image_manager.get_all_images():
                if img != image:
                    # Propagate to all other images, ignore target

                    for star in stars:
                        with self.progress_handler("Finding stars in image..."):
                            star_data = image_manager.find_nearest_star(star.x, star.y)

                        if star_data:
                            measurement = StarMeasurement(
                                x=star_data["xcentroid"],
                                y=star_data["ycentroid"],
                                time=img.observation_time,
                                image=img.filename,
                            )
                            self.measure_manager.add_measurement(measurement)

    @Slot()
    def differential_image(self, image_name: str | None = None):
        """Calculates differential photometry on all measurements in image"""
        if image_name is None:
            if self.image_manager.active_image is None:
                return  # No work to do
            image_name = self.image_manager.active_image.filename

        measurements = self.measure_manager.get_all_measurements(image_name)

        for m in measurements:
            # This could be a better algorithm
            other_ms = [n for n in measurements if n != m]
            calculate_differential_magnitude(m, other_ms)

    @Slot()
    def differential_all(self):
        """Calculates differential photometry on all images' measurements"""
        for image in self.image_manager.get_all_images():
            self.differential_image(image.filename)
