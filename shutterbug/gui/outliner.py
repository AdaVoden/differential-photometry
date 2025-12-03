from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shutterbug.gui.main_window import MainWindow

import logging

from PySide6.QtCore import QItemSelection, QPoint, Qt, Signal, Slot
from PySide6.QtWidgets import QMenu, QTreeView, QVBoxLayout, QWidget
from shutterbug.core.models import OutlinerModel


class Outliner(QWidget):

    object_selected = Signal(object)

    def __init__(self, main_window: MainWindow):
        super().__init__()
        self.setObjectName("outliner")

        # Keep
        self.main_window = main_window

        # Set layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        # Remove layout styling
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Create a file list and connect it here
        self.item_view = QTreeView()
        self.item_view.setHeaderHidden(True)
        self.model = OutlinerModel()
        self.item_view.setModel(self.model)
        self.item_view.alternatingRowColors()
        layout.addWidget(self.item_view)

        # Set up right-click context menu
        self.item_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.item_view.customContextMenuRequested.connect(self.show_context_menu)

        self.item_view.selectionModel().selectionChanged.connect(
            self._on_selection_changed
        )

        # Handle signals
        self.main_window.image_added.connect(self.model.add_image)
        self.main_window.graph_added.connect(self.model.add_graph)
        self.main_window.star_added.connect(self.model.add_star)

        logging.debug("Outliner initialized")

    @Slot(QItemSelection, QItemSelection)
    def _on_selection_changed(self, selected: QItemSelection, _: QItemSelection):
        """Emits the selected data object from outliner click"""
        # Get from internal list
        s = selected.indexes()[0]
        # Data stored in item
        data = s.data(Qt.ItemDataRole.UserRole)
        if data is None:
            return  # No need to do anything
        self.main_window.selection_manager.set_selected_object(data)

    @Slot(QPoint)
    def show_context_menu(self, pos: QPoint):
        """Displays context menu for right-clicked item in file list"""
        selection = self.item_view.selectionModel().selection()
        menu = QMenu()

        delete_action = menu.addAction("Delete")

        menu.exec(self.item_view.mapToGlobal(pos))
