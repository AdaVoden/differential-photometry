from __future__ import annotations

from typing import TYPE_CHECKING

from shutterbug.core.events.change_event import Event, EventDomain
from shutterbug.core.models.star_identity import StarIdentity

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

from typing import Dict

from shutterbug.core.models.graph_model import GraphDataModel
import logging

from .base_manager import BaseManager


class GraphManager(BaseManager):
    """Keeps records of graph data and which is active at any given time"""

    def __init__(self, controller: AppController, parent=None):

        super().__init__(controller, parent)
        self.graphs: Dict[str, GraphDataModel] = {}
        self._ids = []

        logging.debug("Graph Manager initialized")

    def add_graph(self, graph: GraphDataModel):
        self.graphs[graph.uid] = graph
        self.controller.dispatch(Event(EventDomain.GRAPH, "created", data=graph))

    def remove_graph(self, graph: GraphDataModel):
        if graph.uid in self.graphs:
            self.graphs.pop(graph.uid)
            self.controller.dispatch(Event(EventDomain.GRAPH, "removed", data=graph))

    def create_from_star(self, star: StarIdentity):
        """Creates a graph from a given star and adds it to the manager"""
        label = self._new_label()
        graph = GraphDataModel.from_star(label, self.controller, star)
        self.add_graph(graph)
        return graph

    def _new_label(self):
        """Creates new number for default graph labels"""
        if not self._ids:
            # No other ids
            self._ids.append(1)
            return "graph_001"
        new_id = self._ids[-1] + 1
        self._ids.append(new_id)
        return f"graph_{new_id:03}"
