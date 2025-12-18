from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Signal, Slot, Qt
from PySide6.QtGui import QAction

from shutterbug.gui.base_ui_widget import BaseUIWidget

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

from PySide6.QtWidgets import QComboBox, QHBoxLayout, QMenu, QMenuBar, QVBoxLayout

from .views.registry import VIEW_REGISTRY


class Panel(BaseUIWidget):
    """Contains view"""

    split_requested = Signal(Qt.Orientation)
    collapse_requested = Signal(object)

    def __init__(self, name: str, controller: AppController, parent=None):
        super().__init__(controller, parent)
        # Initial variables
        self.name = name
        self.view = VIEW_REGISTRY[name](controller, self)
        self.view.on_activated()
        self.bar_items = []
        self.setObjectName("panel")

        # Set up top bar
        self.bar = BaseUIWidget(controller, self)
        self.bar.setObjectName("topbar")
        # Layout settings
        self.bar_layout = QHBoxLayout(self.bar)
        self.bar_layout.setContentsMargins(2, 2, 1, 1)
        self.bar_layout.setSpacing(2)
        self.bar_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Selector
        self.selector = QComboBox(self)
        self.selector.addItems(list(VIEW_REGISTRY.keys()))
        self.bar_layout.addWidget(self.selector)
        idx = self.selector.findText(name)
        self.selector.setCurrentIndex(idx)
        # Menu
        self.menu_bar = QMenuBar(self)
        self.bar_layout.addWidget(self.menu_bar)

        self._set_panel_items()
        self._setup_region_menu()
        # Fill the rest of the width
        self.bar_layout.addStretch()

        # Layout with styling
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        layout.addWidget(self.bar)
        layout.addWidget(self.view)

        # Styling
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(2)

        self.selector.currentIndexChanged.connect(self._change_view)

    def on_deactivated(self):
        """Handles panel being destroyed"""
        super().on_deactivated()
        if self.view:
            self.view.on_deactivated()

    def _setup_region_menu(self):
        """Sets up region-specific controls in the top bar"""
        split_menu = QMenu("Region", self)

        split_H = split_menu.addAction("Split (Horizontal)")
        split_V = split_menu.addAction("Split (Vertical)")

        split_menu.addSeparator()
        collapse = split_menu.addAction("Collapse")

        # Set up signal events
        split_H.triggered.connect(
            lambda: self.split_requested.emit(Qt.Orientation.Horizontal)
        )
        split_V.triggered.connect(
            lambda: self.split_requested.emit(Qt.Orientation.Vertical)
        )
        collapse.triggered.connect(lambda: self.collapse_requested.emit(self.parent()))

        action = self.menu_bar.addMenu(split_menu)
        self.bar_items.append(action)

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
            self._remove_panel_items()
        layout = self.layout()
        if layout:
            layout.addWidget(self.view)
            self.view.on_activated()
            self._set_panel_items()
            self._setup_region_menu()

        logging.debug(f"Panel containing view {self.view.name} initialized")

    def _set_panel_items(self):
        """Adds view items to panel bar"""
        for item in self.view.create_header_actions():
            if isinstance(item, QMenu):
                # Gives back QAction to remove later
                item = self.menu_bar.addMenu(item)
            else:
                self.bar_layout.addWidget(item)

            self.bar_items.append(item)

    def _remove_panel_items(self):
        """Removes all items added to panel bar"""
        for item in self.bar_items:
            if isinstance(item, QAction):
                self.menu_bar.removeAction(item)
            else:
                self.bar_layout.removeWidget(item)

            item.deleteLater()

        self.bar_items.clear()

    @Slot(int)
    def _change_view(self, idx: int):
        name = self.selector.itemText(idx)
        self.set_view(name)
