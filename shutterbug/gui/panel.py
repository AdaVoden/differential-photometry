from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Slot

from shutterbug.gui.base_ui_widget import BaseUIWidget
from shutterbug.gui.views.base_view import BaseView

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

from PySide6.QtWidgets import QComboBox, QHBoxLayout, QVBoxLayout

from .views.registry import VIEW_REGISTRY


class Panel(BaseUIWidget):
    """Contains view"""

    def __init__(self, view: BaseView, controller: AppController, parent=None):
        super().__init__(controller, parent)
        # Initial variables
        self.view = view
        self.setObjectName("panel")

        # Set up top bar
        self.bar = QHBoxLayout()
        self.bar.setObjectName("topbar")

        # Selector
        self.selector = QComboBox(self)
        self.selector.addItems(list(VIEW_REGISTRY.keys()))
        idx = self.selector.findText(view.name)
        self.selector.setCurrentIndex(idx)
        self.bar.addWidget(self.selector)

        # Fill the rest of the width
        self.bar.addStretch()

        # Layout with styling
        layout = QVBoxLayout(self)
        layout.addLayout(self.bar)
        self.setLayout(layout)

        # Styling
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(2)

        layout.addWidget(self.view)
        self.view.on_activated()

        self.selector.currentIndexChanged.connect(self._change_view)
        logging.debug(f"Panel containing view {view.name} initialized")

    def set_view(self, name: str):
        """Sets view to specified"""
        # Set new view
        old_view = self.view
        self.view = VIEW_REGISTRY[name](self.controller, self)
        # Delete old view
        old_view.on_deactivated()
        old_view.deleteLater()
        layout = self.layout()
        if layout:
            layout.addWidget(self.view)
            self.view.on_activated()

    @Slot(int)
    def _change_view(self, idx: int):
        name = self.selector.itemText(idx)
        self.set_view(name)
