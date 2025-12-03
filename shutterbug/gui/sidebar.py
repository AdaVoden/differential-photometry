import logging

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget
from shutterbug.core.app_controller import AppController
from shutterbug.gui.outliner import Outliner
from shutterbug.gui.properties import Properties


class Sidebar(QWidget):

    object_selected = Signal(object)

    def __init__(self, controller: AppController):
        super().__init__()
        # Initialize sidebar components here
        self.setObjectName("sidebar")

        layout = QVBoxLayout()
        # Remove layout styling
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        # Outliner on top, Settings below
        self.outliner = Outliner(controller)
        self.settings = Properties(controller)

        layout.addWidget(self.outliner, stretch=1)
        layout.addWidget(self.settings, stretch=3)
        self.setLayout(layout)

        # pass up signals
        self.outliner.object_selected.connect(self.object_selected)

        logging.debug("Sidebar initialized")
