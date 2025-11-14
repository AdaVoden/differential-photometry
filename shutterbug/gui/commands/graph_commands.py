from PySide6.QtGui import QUndoCommand

from shutterbug.core.models.graph_model import GraphDataModel


class SelectGraphCommand(QUndoCommand):

    def __init__(self, graph: GraphDataModel):
        super().__init__()
        self.graph = graph

    def redo(self):
        pass

    def undo(self):
        pass


class DeselectGraphCommand(QUndoCommand):

    def __init__(self, graph: GraphDataModel):
        super().__init__()
        self.graph = graph

    def redo(self):
        pass

    def undo(self):
        pass
