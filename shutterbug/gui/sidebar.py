import logging

from PySide6.QtCore import QItemSelection, Signal
from PySide6.QtGui import QUndoStack
from PySide6.QtWidgets import QVBoxLayout, QWidget
from shutterbug.gui.outliner import Outliner
from shutterbug.gui.tool_settings import Settings


class Sidebar(QWidget):

    selection_changed = Signal(QItemSelection, QItemSelection)

    def __init__(self, undo_stack: QUndoStack):
        super().__init__()
        # Initialize sidebar components here
        self.setObjectName("sidebar")

        layout = QVBoxLayout()
        # Remove layout styling
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        # Outliner on top, Settings below
        self.outliner = Outliner(undo_stack)
        self.settings = Settings(undo_stack)

        layout.addWidget(self.outliner, stretch=1)
        layout.addWidget(self.settings, stretch=3)
        self.setLayout(layout)

        # pass up signals
        self.outliner.selection_changed.connect(self.selection_changed)

        logging.debug("Sidebar initialized")
