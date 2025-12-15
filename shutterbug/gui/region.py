from PySide6.QtWidgets import QWidget

from shutterbug.gui.panel import Panel


class Region(QWidget):
    def __init__(self, panel: Panel, parent=None):
        super().__init__(parent)
        self.panel = panel
        self.is_leaf = True
        self.splitter = None

    def split(self, orientation):
        pass

    def collapse(self, region):
        pass
