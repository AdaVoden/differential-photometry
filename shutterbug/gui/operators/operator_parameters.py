from PySide6.QtCore import QObject, Signal


class OperatorParameters(QObject):
    changed = Signal()


class BoxSelectParameters(OperatorParameters):
    threshold = 3.0
