from typing import List

from PySide6.QtGui import QStandardItem
from shutterbug.core.models import FITSModel, StarMeasurement
from shutterbug.core.managers import (
    MeasurementManager,
    StarCatalog,
)
from shutterbug.gui.adapters.tabular_data_interface import TabularDataInterface


class StarMeasurementAdapter(TabularDataInterface):

    def __init__(
        self,
        image: FITSModel,
        measurement_manager: MeasurementManager,
        catalog: StarCatalog,
    ):
        self.image = image
        self.measurement_manager = measurement_manager
        self.catalog = catalog

    def get_column_headers(self) -> List[str]:
        """Gets column information for star measurements"""
        return [
            "ID",
            "X",
            "Y",
            "Flux",
            "Flux Err",
            "Mag",
            "Mag Err",
            "Diff Mag",
            "Diff Mag Err",
        ]

    def get_row_data(self):
        """Gets row data for star measurements"""
        pass

    def _load_all_stars(self):
        """Loads all stars from the Star Manager into table"""
        rows = []
        for star in self.measurement_manager.get_all_measurements(self.image.filename):

            star_id = self.catalog.get_by_measurement(star)
            if star_id:
                row = self._data_to_row(star, star_id.id)
                rows.append(row)

        return rows

    def _data_to_row(self, star: StarMeasurement, star_id: str) -> List[QStandardItem]:
        """Converts a star object to a model row"""
        row = [
            QStandardItem(star_id),
            QStandardItem(self._float_to_str(star.x)),
            QStandardItem(self._float_to_str(star.y)),
            QStandardItem(self._float_to_str(star.flux)),
            QStandardItem(self._float_to_str(star.flux_error)),
            QStandardItem(self._float_to_str(star.mag)),
            QStandardItem(self._float_to_str(star.mag_error)),
            QStandardItem(self._float_to_str(star.diff_mag)),
            QStandardItem(self._float_to_str(star.diff_err)),
        ]
        return row

    def _float_to_str(self, item: float | None) -> str:
        """Converts a float to a string"""
        return "" if item is None else f"{item:.2f}"
