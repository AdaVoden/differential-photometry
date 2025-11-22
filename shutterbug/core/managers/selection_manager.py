import logging
from typing import Any

from PySide6.QtCore import QObject, Signal, Slot
from shutterbug.core.models import (
    FITSModel,
    GraphDataModel,
    StarIdentity,
    StarMeasurement,
)
from shutterbug.gui.adapters.adapter_registry import AdapterRegistry
from shutterbug.gui.adapters.tabular_data_interface import TabularDataInterface


class SelectionManager(QObject):
    adapter_changed = Signal(TabularDataInterface)
    image_selected = Signal(FITSModel)
    graph_selected = Signal(GraphDataModel)
    star_selected = Signal(StarIdentity)
    measurement_selected = Signal(StarMeasurement)

    _instance = None

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self.adapter_registry = AdapterRegistry()
            self._current = None
            super().__init__()

    def __new__(cls):
        if cls._instance is None:
            logging.debug("Creating Selection Manager singleton")
            cls._instance = super().__new__(cls)

        return cls._instance

    @Slot(object)
    def set_selected_object(self, selected: Any):
        """Sets selected object in program"""
        self._current = selected
        logging.debug(f"Attempting to find adapter for {type(selected).__name__}")
        adapter = self.adapter_registry.get_adapter_for(selected)
        if adapter is not None:
            logging.debug("Adapter found")
            self.adapter_changed.emit(adapter)
        else:
            logging.error(f"Failed to find adapter for {type(selected).__name__}")

        # Still ought to be a better way
        if isinstance(selected, FITSModel):
            self.image_selected.emit(selected)
        elif isinstance(selected, GraphDataModel):
            self.graph_selected.emit(selected)
        elif isinstance(selected, StarIdentity):
            self.star_selected.emit(selected)
        elif isinstance(selected, StarMeasurement):
            self.measurement_selected.emit(selected)
