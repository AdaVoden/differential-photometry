from PySide6.QtGui import QUndoCommand


class BaseCommand(QUndoCommand):

    def __init__(self):
        super().__init__()

    def validate(self):
        """Validates that command can run"""
        raise NotImplementedError
