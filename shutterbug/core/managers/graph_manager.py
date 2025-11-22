from typing import Dict
from PySide6.QtCore import QObject, Signal

from shutterbug.core.models.graph_model import GraphDataModel
import logging


class GraphManager(QObject):
    """Keeps records of graph data and which is active at any given time"""

    _instance = None

    graph_added = Signal(GraphDataModel)
    active_graph_changed = Signal(GraphDataModel)
    graph_removed = Signal(GraphDataModel)

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True

            super().__init__()
            self.graphs: Dict[str, GraphDataModel] = {}
            self.active_graph: GraphDataModel | None = None

    def __new__(cls):
        if cls._instance is None:
            logging.debug("Creating Graph Manager singleton")
            cls._instance = super().__new__(cls)

        return cls._instance

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
