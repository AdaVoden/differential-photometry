import logging

from PySide6.QtWidgets import QVBoxLayout
from shutterbug.core.app_controller import AppController
from shutterbug.gui.base_ui_widget import BaseUIWidget
from shutterbug.gui.panel import Panel


class Sidebar(BaseUIWidget):

    def __init__(self, controller: AppController, parent=None):
        super().__init__(controller, parent)
        # Initialize sidebar components here
        self.setObjectName("sidebar")

        layout = QVBoxLayout()
        # Remove layout styling
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        # Outliner on top, Settings below

        layout.addWidget(Panel("Outliner", self.controller, self), stretch=1)
        layout.addWidget(Panel("Properties", self.controller, self), stretch=3)
        self.setLayout(layout)

        logging.debug("Sidebar initialized")
