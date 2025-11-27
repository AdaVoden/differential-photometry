from PySide6.QtCore import QObject, Signal


class OperatorParameters(QObject):
    changed = Signal()


class BoxSelectParameters(OperatorParameters):
    def __init__(self):
        super().__init__()
        self.threshold = 3.0
