import logging
from typing import Any
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QUndoStack

from shutterbug.core.models import (
    FITSModel,
    GraphDataModel,
    StarIdentity,
    StarMeasurement,
)
from shutterbug.gui.adapters.tabular_data_interface import TabularDataInterface
from shutterbug.gui.commands import (
    SelectFileCommand,
    SelectGraphCommand,
    SelectStarCommand,
)


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

            super().__init__()

    def __new__(cls, undo_stack: QUndoStack):
        if cls._instance is None:
            logging.debug("Creating Selection Manager singleton")
            cls._instance = super().__new__(cls)

            cls._undo_stack = undo_stack
        return cls._instance

    @Slot(object)
    def set_selected_object(self, selected: Any):
        """Sets selected object in program"""
        stack = self._undo_stack
        if isinstance(selected, FITSModel):
            stack.push(
                SelectFileCommand(
                    selected_image=selected,
                )
            )
        elif isinstance(selected, GraphDataModel):
            stack.push(SelectGraphCommand(graph=selected))
        elif isinstance(selected, StarIdentity):
            stack.push(SelectStarCommand(identity=selected))
