from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

import logging
from typing import List

from PySide6.QtCore import Slot
from PySide6.QtGui import QStandardItem
from shutterbug.core.models import FITSModel, StarMeasurement
from shutterbug.gui.adapters.tabular_data_interface import (
    AdapterSignals,
    TabularDataInterface,
)


class FITSModelAdapter(TabularDataInterface):

    def __init__(self, image: FITSModel, controller: AppController):
        self.image = image
        self.controller = controller
        self.catalog = controller.stars
        self._signals = AdapterSignals()

        # Set up signals
        self.catalog.measurement_added.connect(self._on_measurement_added)
        self.catalog.measurement_updated.connect(self._on_measurement_changed)
        self.catalog.measurement_removed.connect(self._on_measurement_removed)

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

    def get_row_data(self) -> List:
        """Gets row data for star measurements"""
        return self._load_all_stars()

    @property
    def signals(self) -> AdapterSignals:
        """Provides signals for the adapter"""
        return self._signals

    def _load_all_stars(self):
        """Loads all stars from the Star Catalog into table"""
        rows = []
        for star in self.catalog.get_all_stars():
            measurement = star.measurements.get(self.image.filename)
            if measurement is not None:
                row = self._get_row_from_measurement(measurement)
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

    def _get_row_from_measurement(self, measurement: StarMeasurement):
        """Gets ID from catalog and returns the row"""
        star_id = self.catalog.get_by_measurement(measurement)
        if star_id is None:
            logging.error("Adapter unable to get catalog star id from measurement")
            return
        return self._data_to_row(measurement, star_id.id)

    @Slot(StarMeasurement)
    def _on_measurement_changed(self, measurement: StarMeasurement):
        """Handles measurement being changed"""
        self.signals.item_updated.emit(self._get_row_from_measurement(measurement))

    @Slot(StarMeasurement)
    def _on_measurement_added(self, measurement: StarMeasurement):
        """Handles measurement being added to image"""
        self.signals.item_added.emit(self._get_row_from_measurement(measurement))

    @Slot(StarMeasurement)
    def _on_measurement_removed(self, measurement: StarMeasurement):
        """Handles measurement being removed from image"""
        self.signals.item_removed.emit(self._get_row_from_measurement(measurement))
