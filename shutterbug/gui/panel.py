from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import Slot

from shutterbug.gui.base_ui_widget import BaseUIWidget
from shutterbug.gui.views.base_view import BaseView

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

from PySide6.QtWidgets import QComboBox, QHBoxLayout, QVBoxLayout

from .views.registry import VIEW_REGISTRY


class Panel(BaseUIWidget):
    """Contains view"""

    def __init__(self, name: str, controller: AppController, parent=None):
        super().__init__(controller, parent)
        # Initial variables
        self.name = name
        self.view = VIEW_REGISTRY[name](controller, self)
        self.view.on_activated()
        self.setObjectName("panel")

        # Set up top bar
        self.bar = QHBoxLayout()
        self.bar.setObjectName("topbar")

        # Selector
        self.selector = QComboBox(self)
        self.selector.addItems(list(VIEW_REGISTRY.keys()))
        self.bar.addWidget(self.selector)
        idx = self.selector.findText(name)
        self.selector.setCurrentIndex(idx)

        # Fill the rest of the width
        self.bar.addStretch()

        # Layout with styling
        layout = QVBoxLayout(self)
        layout.addLayout(self.bar)
        self.setLayout(layout)
        layout.addWidget(self.view)

        # Styling
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(2)

        self.selector.currentIndexChanged.connect(self._change_view)

    def set_view(self, name: str):
        """Sets view to specified"""
        # Set new view
        self.name = name
        old_view = self.view
        self.view = VIEW_REGISTRY[name](self.controller, self)
        # Delete old view
        if old_view:
            old_view.on_deactivated()
            old_view.deleteLater()
        layout = self.layout()
        if layout:
            layout.addWidget(self.view)
            self.view.on_activated()

        logging.debug(f"Panel containing view {self.view.name} initialized")

    @Slot(int)
    def _change_view(self, idx: int):
        name = self.selector.itemText(idx)
        self.set_view(name)
