from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from shutterbug.core.events.change_event import Event, EventDomain

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

import logging
from typing import Any

from PySide6.QtCore import Slot
from shutterbug.core.managers.base_manager import BaseManager
from shutterbug.core.models import (
    FITSModel,
    GraphDataModel,
    StarIdentity,
    StarMeasurement,
)


@dataclass
class SelectionContext:
    image: Optional[FITSModel] = None
    star: Optional[StarIdentity] = None
    graph: Optional[GraphDataModel] = None
    measurement: Optional[StarMeasurement] = None


class SelectionManager(BaseManager):

    def __init__(self, controller: AppController, parent=None):

        super().__init__(controller, parent)
        self.adapter_registry = controller.adapters
        self._context = SelectionContext
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
            if self._context.image:
                self.controller.dispatch(
                    Event(EventDomain.IMAGE, "deselected", data=self._context.image)
                )
            self._context.image = selected
            self.controller.dispatch(
                Event(EventDomain.IMAGE, "selected", data=selected)
            )
        elif isinstance(selected, GraphDataModel):
            if self._context.graph:
                self.controller.dispatch(
                    Event(EventDomain.GRAPH, "deselected", data=self._context.graph)
                )

            self._context.graph = selected
            self.controller.dispatch(
                Event(EventDomain.GRAPH, "selected", data=selected)
            )
        elif isinstance(selected, StarIdentity):
            if self._context.star:
                self.controller.dispatch(
                    Event(EventDomain.STAR, "deselected", data=self._context.star)
                )

            self._context.star = selected
            self.controller.dispatch(Event(EventDomain.STAR, "selected", data=selected))

        elif isinstance(selected, StarMeasurement):
            if self._context.measurement:
                self.controller.dispatch(
                    Event(
                        EventDomain.MEASUREMENT,
                        "deselected",
                        data=self._context.measurement,
                    )
                )

            self._context.measurement = selected
            self.controller.dispatch(
                Event(EventDomain.MEASUREMENT, "selected", data=selected)
            )

    @property
    def star(self):
        return self._context.star

    @property
    def image(self):
        return self._context.image

    @property
    def graph(self):
        return self._context.graph

    @property
    def measurement(self):
        return self._context.measurement
