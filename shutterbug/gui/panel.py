from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Signal, Slot, Qt

from shutterbug.gui.base_ui_widget import BaseUIWidget

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

from PySide6.QtWidgets import QComboBox, QHBoxLayout, QMenu, QMenuBar, QVBoxLayout

from .views.registry import VIEW_REGISTRY


class Panel(BaseUIWidget):
    """Contains view"""

    split_requested = Signal(Qt.Orientation)

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
        # Menu
        self.menu_bar = QMenuBar()
        self.bar.addWidget(self.menu_bar)
        for menu in self.view.create_header_actions():
            self.menu_bar.addMenu(menu)

        self._setup_region_menu()

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

    def _setup_region_menu(self):
        """Sets up region-specific controls in the top bar"""
        split_menu = QMenu("Region", self)

        split_H = split_menu.addAction("Split (Horizontal)")
        split_V = split_menu.addAction("Split (Vertical)")

        split_menu.addSeparator()
        collapse_H = split_menu.addAction("Collapse (Horizontal)")
        colllapse_V = split_menu.addAction("Collapse (Vertical)")

        # Set up signal events
        split_H.triggered.connect(
            lambda: self.split_requested.emit(Qt.Orientation.Horizontal)
        )
        split_V.triggered.connect(
            lambda: self.split_requested.emit(Qt.Orientation.Vertical)
        )

        self.menu_bar.addMenu(split_menu)

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
