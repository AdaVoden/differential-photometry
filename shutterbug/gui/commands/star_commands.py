from PySide6.QtGui import QUndoCommand


class SelectStar(QUndoCommand):
    """Command to select a star"""

    def __init__(self):
        super().__init__()

    def redo(self):
        pass

    def undo(self):
        pass


class DeselectStar(QUndoCommand):
    """Command to deselect a star"""

    def __init__(self):
        super().__init__()

    def redo(self):
        pass

    def undo(self):
        pass
