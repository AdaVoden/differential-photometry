import logging

from typing import List

from PySide6.QtCore import Slot
from PySide6.QtGui import QStandardItem

from shutterbug.core.managers import StarCatalog
from shutterbug.core.models import StarIdentity
from shutterbug.core.models.star_measurement import StarMeasurement
from shutterbug.gui.adapters.tabular_data_interface import (
    TabularDataInterface,
    AdapterSignals,
)


class StarIdentityAdapter(TabularDataInterface):
    def __init__(self, star: StarIdentity):
        self.star = star
        self.catalog = StarCatalog()
        self._signals = AdapterSignals()

        # Set up signals
        self.catalog.measurement_added.connect(self._on_measurement_added)
        self.catalog.measurement_updated.connect(self._on_measurement_changed)
        self.catalog.measurement_removed.connect(self._on_measurement_removed)

    def get_column_headers(self) -> List[str]:
        """Gets column information for star measurements"""
        return [
            "Image",
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
        return self._load_all_measurements()

    @property
    def signals(self) -> AdapterSignals:
        """Provides signals for the adapter"""
        return self._signals

    def _load_all_measurements(self) -> List[QStandardItem]:
        """Loads all measurements from star into table"""
        rows = []
        for measurement in self.star.measurements.values():
            row = self._data_to_row(measurement)
            rows.append(row)
        return rows

    def _data_to_row(self, star: StarMeasurement) -> List[QStandardItem]:
        """Converts star measurement to data row for display in spreadsheet"""
        row = [
            QStandardItem(star.image),
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
        return "" if item is None else f"{item:.2f}"

    @Slot(StarMeasurement)
    def _on_measurement_changed(self, measurement: StarMeasurement):
        """Handles measurement being changed"""
        self.signals.item_updated.emit(self._data_to_row(measurement))

    @Slot(StarMeasurement)
    def _on_measurement_added(self, measurement: StarMeasurement):
        """Handles measurement being added to image"""
        self.signals.item_added.emit(self._data_to_row(measurement))

    @Slot(StarMeasurement)
    def _on_measurement_removed(self, measurement: StarMeasurement):
        """Handles measurement being removed from image"""
        self.signals.item_removed.emit(self._data_to_row(measurement))
