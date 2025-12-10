from __future__ import annotations

from typing import TYPE_CHECKING

from shutterbug.core.events.change_event import Event

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

import logging

from typing import List

from PySide6.QtCore import Slot
from PySide6.QtGui import QStandardItem

from shutterbug.core.models import StarIdentity
from shutterbug.core.models.star_measurement import StarMeasurement
from shutterbug.gui.adapters.tabular_data_interface import (
    TabularDataInterface,
    AdapterSignals,
)


class StarIdentityAdapter(TabularDataInterface):

    # Map field name to column
    mapping = {
        "x": 1,
        "y": 2,
        "flux": 3,
        "flux_error": 4,
        "mag": 5,
        "mag_error": 6,
        "diff_mag": 7,
        "diff_err": 8,
    }

    def __init__(self, star: StarIdentity, controller: AppController):
        self.star = star
        self.controller = controller
        self._signals = AdapterSignals()

        # Set up signals
        self.controller.on("measurement.created", self._on_measurement_added)
        self.controller.on("measurement.updated.*", self._on_measurement_changed)
        self.controller.on("measurement.removed", self._on_measurement_removed)

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
            QStandardItem(star.image_id),
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

    @Slot(Event)
    def _on_measurement_changed(self, event: Event):
        """Handles measurement being changed"""
        measurement = event.data
        if measurement is None or event.field is None:
            return
        if measurement not in self.star.measurements:
            return  # It's a measurement we don't care about

        self.signals.item_updated.emit(
            measurement.image,
            self.mapping[event.field],
            getattr(measurement, event.field),
        )

    @Slot(Event)
    def _on_measurement_added(self, event: Event):
        """Handles measurement being added to image"""
        measurement = event.data
        if measurement is None:
            return
        if measurement not in self.star.measurements:
            return  # It's a measurement we don't care about
        self.signals.item_added.emit(self._data_to_row(measurement))

    @Slot(Event)
    def _on_measurement_removed(self, event: Event):
        """Handles measurement being removed from image"""
        measurement = event.data
        if measurement is None:
            return
        if measurement not in self.star.measurements:
            return  # It's a measurement we don't care about

        self.signals.item_removed.emit(measurement.image)
