import logging

from PySide6.QtCore import QCoreApplication, Slot
from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProgressBar,
    QWidget,
)
from shutterbug.core.app_controller import AppController
from shutterbug.gui.managers.progress_manager import ProgressTask
from shutterbug.gui.region import Region


from .commands import LoadImagesCommand
from .project import ShutterbugProject
from .panel import Panel


class MainWindow(QMainWindow):

    def __init__(self, controller: AppController):
        super().__init__()
        self.setObjectName("mainWindow")
        # Set window properties
        self.setWindowTitle("Shutterbug")
        self.setGeometry(100, 100, 1200, 800)

        self.controller = controller
        # Set up save/load functionality
        self.project = ShutterbugProject()

        # Set up central widget with horizontal layout
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout()
        central.setLayout(main_layout)

        # Remove styling from layouts
        main_layout.setContentsMargins(1, 1, 1, 1)
        main_layout.setSpacing(2)

        # Set up default layout
        image_viewer = Panel("Image Viewer", self.controller)
        outliner = Panel("Outliner", self.controller)
        properties = Panel("Properties", self.controller)

        region_main = Region(image_viewer)
        region_main.split(Qt.Orientation.Horizontal, 3, 1)
        region_main.child_b.set_panel(outliner)
        region_main.child_b.split(Qt.Orientation.Vertical, 1, 3)
        region_main.child_b.child_b.set_panel(properties)

        main_layout.addWidget(region_main)

        # Set up menu bar
        self.setup_menu_bar()

        # Set up status bar
        self.status_bar = self.statusBar()
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

        # Set up progress bar (Hidden by default)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMaximumWidth(100)  # Pixels
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setMinimum(0)
        # Handler for context handling
        self.progress = controller.progress

        # Add to status bar
        self.status_bar.addPermanentWidget(self.progress_bar)

        self.progress.started.connect(self._on_progress_started)
        self.progress.finished.connect(self._on_progress_finished)
        self.progress.changed.connect(self._on_progress_changed)

        logging.debug("Main window initialized")

    @Slot(ProgressTask)
    def _on_progress_started(self, progress: ProgressTask):
        """Handles progress task starting"""
        self.progress_bar.setVisible(True)
        self._update_progress_bar(progress)
        self.status_label.setText(progress.text)
        self.status_label.repaint()

    @Slot()
    def _on_progress_finished(self):
        """Handles progress task finishing"""
        self.status_label.setText("Ready")
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)

    @Slot(ProgressTask)
    def _on_progress_changed(self, progress: ProgressTask):
        """Handles text changing in progress handler"""
        self._update_progress_bar(progress)
        self.status_label.setText(progress.text)
        self.status_label.repaint()

    def _update_progress_bar(self, progress: ProgressTask):
        """Updates the progress bar"""
        self.progress_bar.setValue(progress.percent)
        self.progress_bar.repaint()
        self.status_bar.repaint()

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

        self.controller._undo_stack.push(LoadImagesCommand(filenames, self.controller))

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
