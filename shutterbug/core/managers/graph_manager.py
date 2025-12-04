from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

from typing import Dict
from PySide6.QtCore import Signal

from shutterbug.core.models.graph_model import GraphDataModel
import logging

from .base_manager import BaseManager


class GraphManager(BaseManager):
    """Keeps records of graph data and which is active at any given time"""

    graph_added = Signal(GraphDataModel)
    active_graph_changed = Signal(GraphDataModel)
    graph_removed = Signal(GraphDataModel)

    def __init__(self, controller: AppController, parent=None):

        super().__init__(controller, parent)
        self.graphs: Dict[str, GraphDataModel] = {}
        self.active_graph: GraphDataModel | None = None

        logging.debug("Graph Manager initialized")

    def add_graph(self, graph: GraphDataModel):
        self.graphs[graph.uid] = graph
        self.graph_added.emit(graph)

    def remove_graph(self, graph: GraphDataModel):
        if graph.uid in self.graphs:
            self.graphs.pop(graph.uid)
            self.graph_removed.emit(graph)

    def set_active_graph(self, graph: GraphDataModel | None):
        if self.active_graph != graph:
            if graph is None:
                logging.debug(f"Setting active graph to none")
            else:
                logging.debug(f"Setting active graph to {graph.uid}")
            self.active_graph = graph
            self.active_graph_changed.emit(graph)
