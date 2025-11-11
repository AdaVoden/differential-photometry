import logging
from PySide6.QtWidgets import QVBoxLayout, QWidget, QTableView, QHeaderView
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtCore import QModelIndex, Slot

from shutterbug.core.models import FITSModel, StarMeasurement
from shutterbug.core.managers import ImageManager, StarCatalog


class SpreadsheetViewer(QWidget):
    """Viewer for star data in spreadsheet format"""

    def __init__(self):
        super().__init__()
        # Default variables
        self.image_manager = ImageManager()
        self.current_image = self.image_manager.active_image
        self.catalog = StarCatalog()

        self.header_labels = ["ID", "X", "Y", "Flux", "Flux Err", "Mag", "Mag Err"]

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

        logging.debug("Spreadsheet viewer initialized")

    @Slot(FITSModel)
    def _on_image_change(self, image: FITSModel):
        """Handles the image changing by populating new data and connecting signals"""
        if self.current_image:
            star_manager = self.current_image.star_manager
            star_manager.measurement_added.disconnect(self._on_star_added)
            star_manager.measurement_removed.disconnect(self._on_star_removed)
            star_manager.measurement_changed.disconnect(self._on_star_changed)

        self.current_image = image
        if image:
            logging.debug(f"Spreadsheet changing image to: {image.filename}")
            star_manager = image.star_manager
            star_manager.measurement_added.connect(self._on_star_added)
            star_manager.measurement_removed.connect(self._on_star_removed)
            star_manager.measurement_changed.connect(self._on_star_changed)

            self._load_all_stars()

    @Slot(StarMeasurement)
    def _on_star_added(self, star: StarMeasurement):
        """Handles new star being added to Star Manager"""
        star_id = self.catalog.get_by_measurement(star)
        if star_id:
            logging.debug(f"Spreadsheet adding star id: {star_id.id}")
            row = self._data_to_row(star, star_id.id)
            self.model.appendRow(row)

    @Slot(StarMeasurement)
    def _on_star_removed(self, star: StarMeasurement):
        """Handles star being removed from Star Manager"""
        star_id = self.catalog.get_by_measurement(star)
        if star_id:
            logging.debug(f"Spreadsheet removing star id: {star_id.id}")
            idx = self._idx_from_id(star_id.id)
            if idx:
                self.model.removeRow(idx.row())

    @Slot(object)
    def _on_star_changed(self, star: StarMeasurement):
        """Handles star being changed"""
        star_id = self.catalog.get_by_measurement(star)
        if star_id:
            idx = self._idx_from_id(star_id.id)
            if idx:
                row = idx.row()
                self.model.setItem(row, 3, QStandardItem(self._float_to_str(star.flux)))
                self.model.setItem(
                    row, 4, QStandardItem(self._float_to_str(star.flux_error))
                )
                self.model.setItem(row, 5, QStandardItem(self._float_to_str(star.mag)))
                self.model.setItem(
                    row, 6, QStandardItem(self._float_to_str(star.mag_error))
                )

    def _load_all_stars(self):
        """Loads all stars from the Star Manager into table"""
        self._clear_all()
        if not self.current_image:
            return  # No work to do

        rows = []
        for star in self.current_image.star_manager.get_all_stars():

            star_id = self.catalog.get_by_measurement(star)
            if star_id:
                row = self._data_to_row(star, star_id.id)
                rows.append(row)
        self.model.appendRow(rows)

    def _idx_from_id(self, id: str) -> QModelIndex | None:
        """Finds index associated with id"""
        row = self.model.findItems(id)
        if row:
            idx = self.model.indexFromItem(row[0])
            return idx
        return None

    def _clear_all(self):
        """Clears all items from model and view"""
        self.model.clear()
        self.model.setHorizontalHeaderLabels(self.header_labels)

    def _data_to_row(self, star: StarMeasurement, star_id: str):
        """Converts a star object to a model row"""
        row = [
            QStandardItem(star_id),
            QStandardItem(self._float_to_str(star.x)),
            QStandardItem(self._float_to_str(star.y)),
            QStandardItem(self._float_to_str(star.flux)),
            QStandardItem(self._float_to_str(star.flux_error)),
            QStandardItem(self._float_to_str(star.mag)),
            QStandardItem(self._float_to_str(star.mag_error)),
        ]
        return row

    def _float_to_str(self, item: float | None):
        """Converts a float to a string"""
        return "" if item is None else f"{item:.2f}"
