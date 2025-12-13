import logging

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout
from shutterbug.core.app_controller import AppController
from shutterbug.gui.base_ui_widget import BaseUIWidget
from shutterbug.gui.panel import Panel
from shutterbug.gui.views.outliner import Outliner
from shutterbug.gui.views.properties import Properties


class Sidebar(BaseUIWidget):

    object_selected = Signal(object)

    def __init__(self, controller: AppController, parent=None):
        super().__init__(controller, parent)
        # Initialize sidebar components here
        self.setObjectName("sidebar")

        layout = QVBoxLayout()
        # Remove layout styling
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        # Outliner on top, Settings below
        self.outliner = Outliner(controller)
        self.settings = Properties(controller)

        layout.addWidget(Panel(self.outliner, self.controller, self), stretch=1)
        layout.addWidget(Panel(self.settings, self.controller, self), stretch=3)
        self.setLayout(layout)

        # pass up signals
        self.outliner.object_selected.connect(self.object_selected)

        logging.debug("Sidebar initialized")
