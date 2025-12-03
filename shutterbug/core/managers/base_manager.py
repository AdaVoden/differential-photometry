from PySide6.QtCore import QObject


class BaseManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
