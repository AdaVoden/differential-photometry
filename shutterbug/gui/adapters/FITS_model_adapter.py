from __future__ import annotations

from typing import TYPE_CHECKING

from shutterbug.core.events.change_event import Event

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

    def __init__(self, image: FITSModel, controller: AppController):
        self.image = image
        self.controller = controller
        self._signals = AdapterSignals()

        # Set up signals
        controller.on("measurement.created", self._on_measurement_added)
        controller.on("measurement.updated.*", self._on_measurement_changed)
        controller.on("measurement.removed", self._on_measurement_removed)

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
        for star in self.controller.stars.get_all_stars():
            measurement = star.measurements.get(self.image.uid)
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
        return "" if item is None else f"{item:.3f}"

    def _get_row_from_measurement(self, measurement: StarMeasurement):
        """Gets ID from catalog and returns the row"""
        star_id = self.controller.stars.get_by_measurement(measurement)
        if star_id is None:
            logging.error("Adapter unable to get catalog star id from measurement")
            return
        return self._data_to_row(measurement, star_id.id)

    @Slot(Event)
    def _on_measurement_changed(self, event: Event):
        """Handles measurement being changed"""
        if event.data is None or event.field is None:
            return
        if event.data.image_id != self.image.uid:
            return
        star = self.controller.stars.get_by_measurement(event.data)
        if star is None:
            return
        value = self._float_to_str(getattr(event.data, event.field))
        self.signals.item_updated.emit(star.id, self.mapping[event.field], value)

    @Slot(Event)
    def _on_measurement_added(self, event: Event):
        """Handles measurement being added to image"""
        if event.data is None:
            return

        self.signals.item_added.emit(self._get_row_from_measurement(event.data))

    @Slot(Event)
    def _on_measurement_removed(self, event: Event):
        """Handles measurement being removed from image"""
        if event.data is None:
            return
        star = self.controller.stars.get_by_measurement(event.data)
        if star is None:
            return

        self.signals.item_removed.emit(star.id)
