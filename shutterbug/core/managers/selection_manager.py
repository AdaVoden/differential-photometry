from __future__ import annotations

from typing import TYPE_CHECKING

from shutterbug.core.events.change_event import Event, EventDomain

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

import logging
from typing import Any

from PySide6.QtCore import Signal, Slot
from shutterbug.core.managers.base_manager import BaseManager
from shutterbug.core.models import (
    FITSModel,
    GraphDataModel,
    StarIdentity,
    StarMeasurement,
)
from shutterbug.gui.adapters.tabular_data_interface import TabularDataInterface


class SelectionManager(BaseManager):
    adapter_changed = Signal(TabularDataInterface)
    image_selected = Signal(FITSModel)
    graph_selected = Signal(GraphDataModel)
    star_selected = Signal(StarIdentity)
    measurement_selected = Signal(StarMeasurement)

    _instance = None

    def __init__(self, controller: AppController, parent=None):

        super().__init__(controller, parent)
        self.adapter_registry = controller.adapters
        self._current = None
        logging.debug("Selection Manager initialized")

    @Slot(object)
    def set_selected_object(self, selected: Any):
        """Sets selected object in program"""
        self._current = selected
        logging.debug(f"Attempting to find adapter for {type(selected).__name__}")
        adapter = self.adapter_registry.get_adapter_for(selected)
        if adapter is not None:
            logging.debug("Adapter found")
            self.controller.dispatch(
                Event(EventDomain.ADAPTER, "selected", data=adapter)
            )
        else:
            logging.error(f"Failed to find adapter for {type(selected).__name__}")

        # Still ought to be a better way
        if isinstance(selected, FITSModel):
            self.controller.dispatch(
                Event(EventDomain.IMAGE, "selected", data=selected)
            )
        elif isinstance(selected, GraphDataModel):
            self.controller.dispatch(
                Event(EventDomain.GRAPH, "selected", data=selected)
            )

            self.graph_selected.emit(selected)
        elif isinstance(selected, StarIdentity):
            self.controller.dispatch(Event(EventDomain.STAR, "selected", data=selected))

            self.star_selected.emit(selected)
        elif isinstance(selected, StarMeasurement):
            self.controller.dispatch(
                Event(EventDomain.MEASUREMENT, "selected", data=selected)
            )

            self.measurement_selected.emit(selected)
