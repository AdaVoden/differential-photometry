from PySide6.QtGui import QUndoCommand


class BaseCommand(QUndoCommand):

    def __init__(self, *args):
        super().__init__(*args)

    def validate(self):
        """Validates that command can run"""
        raise NotImplementedError
