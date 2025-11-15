from PySide6.QtGui import QUndoCommand

from shutterbug.core.managers import GraphManager
from shutterbug.core.models.graph_model import GraphDataModel


class SelectGraphCommand(QUndoCommand):

    def __init__(self, graph: GraphDataModel):
        super().__init__()
        self.graph = graph
        self.graph_manager = GraphManager()
        self.old_graph = self.graph_manager.active_graph

    def redo(self):
        self.graph_manager.set_active_graph(self.graph)

    def undo(self):
        self.graph_manager.set_active_graph(self.old_graph)


class DeselectGraphCommand(QUndoCommand):

    def __init__(self):
        super().__init__()
        self.graph_manager = GraphManager()
        self.old_graph = self.graph_manager.active_graph

    def redo(self):
        self.graph_manager.set_active_graph(None)

    def undo(self):
        self.graph_manager.set_active_graph(self.old_graph)
