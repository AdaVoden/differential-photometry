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
        pass

    def remove_graph(self, graph: GraphDataModel):
        pass

    def set_active_graph(self, graph: GraphDataModel):
        pass
