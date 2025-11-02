from PySide6.QtGui import QUndoCommand


class SelectTargetStar(QUndoCommand):
    pass


class DeselectTargetStar(QUndoCommand):
    pass


class SelectReferenceStar(QUndoCommand):
    pass


class DeselectReferenceStar(QUndoCommand):
    pass
