import logging

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QUndoStack

from shutterbug.gui.outliner import Outliner
from shutterbug.gui.tool_settings import Settings
from shutterbug.gui.image_manager import ImageManager


class Sidebar(QWidget):

    def __init__(self, undo_stack: QUndoStack, image_manager: ImageManager):
        super().__init__()
        # Initialize sidebar components here
        self.setObjectName("sidebar")

        layout = QVBoxLayout()
        # Remove layout styling
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        # Outliner on top, Settings below
        self.outliner = Outliner(undo_stack, image_manager)
        self.settings = Settings(undo_stack, image_manager)

        layout.addWidget(self.outliner, stretch=1)
        layout.addWidget(self.settings, stretch=3)
        self.setLayout(layout)

        logging.debug("Sidebar initialized")
