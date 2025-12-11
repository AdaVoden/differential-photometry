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
        self.active_graph: GraphDataModel | None = None

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
        graph = GraphDataModel.from_star(self.controller, star)
        self.add_graph(graph)
        return graph
