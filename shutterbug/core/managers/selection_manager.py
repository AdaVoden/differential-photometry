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
    adapter: Optional[object] = None


class SelectionManager(BaseManager):

    mapping = {
        FITSModel: "image",
        StarIdentity: "star",
        GraphDataModel: "graph",
        StarMeasurement: "star",
    }

    def __init__(self, controller: AppController, parent=None):

        super().__init__(controller, parent)
        self.adapter_registry = controller.adapters
        self._context = SelectionContext()
        logging.debug("Selection Manager initialized")

    @Slot(object)
    def select(self, selected: Any):
        """Sets selected object in program"""
        logging.debug(f"Attempting to find adapter for {type(selected).__name__}")
        adapter = self.adapter_registry.get_adapter_for(selected)
        if adapter is not None:
            logging.debug("Adapter found")
            self.controller.dispatch(
                Event(EventDomain.ADAPTER, "selected", data=adapter)
            )
            self._context.adapter = adapter
        else:
            logging.error(f"Failed to find adapter for {type(selected).__name__}")

        self._change_selection(selected)

    def _change_selection(self, data: Any):
        """Changes selection based on type mapping"""
        data_type = self.mapping.get(type(data))
        # If we have a type, we're golden
        if data_type:
            selection = getattr(self._context, data_type)
            if selection:
                self.controller.dispatch(
                    Event(EventDomain(data_type), "deselected", data=selection)
                )
            setattr(self._context, data_type, data)
            self.controller.dispatch(
                Event(EventDomain(data_type), "selected", data=data)
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
    def adapter(self):
        return self._context.adapter

    def get(self, object: Any):
        """Gets the selection of a given object's type"""
        data_type = self.mapping.get(type(object))
        if data_type:
            return getattr(self._context, data_type)
