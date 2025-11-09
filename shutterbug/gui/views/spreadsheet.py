from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QTableView, QHeaderView
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtCore import Slot, Signal

from shutterbug.gui.image_data import FITSImage
from shutterbug.gui.image_manager import ImageManager
from shutterbug.gui.stars.star import StarMeasurement


class SpreadsheetViewer(QWidget):
    """Viewer for star data in spreadsheet format"""

    def __init__(self):
        super().__init__()
        # Default variables
        self.image_manager = ImageManager()
        self.current_image = self.image_manager.active_image

        self.header_labels = ["X", "Y", "Flux", "Flux Err", "Mag", "Mag Err"]

        # Layout without styling
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # Default model
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(self.header_labels)

        # Table View
        self.table_view = QTableView()
        self.table_view.setModel(self.model)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        layout.addWidget(self.table_view)
        # Connections
        self.image_manager.active_image_changed.connect(self._on_image_change)

    @Slot(FITSImage)
    def _on_image_change(self, image: FITSImage):
        """Handles the image changing by populating new data and connecting signals"""
        if self.current_image:
            star_manager = self.current_image.star_manager
            star_manager.star_added.disconnect(self._on_star_added)
            star_manager.star_removed.disconnect(self._on_star_removed)

        self.current_image = image
        if image:
            star_manager = image.star_manager
            star_manager.star_added.connect(self._on_star_added)
            star_manager.star_removed.connect(self._on_star_removed)

            self._load_all_stars()

    @Slot(StarMeasurement)
    def _on_star_added(self, star: StarMeasurement):
        """Handles new star being added to Star Manager"""
        row = self._data_to_row(star)
        self.model.appendRow(row)

    @Slot(StarMeasurement)
    def _on_star_removed(self):
        """Handles star being removed from Star Manager"""
        pass

    def _load_all_stars(self):
        """Loads all stars from the Star Manager into table"""
        self._clear_all()
        if not self.current_image:
            return  # No work to do

        for star in self.current_image.star_manager.get_all_stars():
            row = self._data_to_row(star)
            self.model.appendRow(row)

    def _clear_all(self):
        """Clears all items from model and view"""
        self.model.clear()
        self.model.setHorizontalHeaderLabels(self.header_labels)

    def _data_to_row(self, star: StarMeasurement):
        """Converts a star object to a model row"""
        row = [
            QStandardItem(self._item_to_str(star.x)),
            QStandardItem(self._item_to_str(star.y)),
            QStandardItem(self._item_to_str(star.flux)),
            QStandardItem(self._item_to_str(star.flux_error)),
            QStandardItem(self._item_to_str(star.mag)),
            QStandardItem(self._item_to_str(star.mag_error)),
        ]
        return row

    def _item_to_str(self, item: float | None):
        """Converts a float to a string"""
        return "" if item is None else f"{item:.2f}"
