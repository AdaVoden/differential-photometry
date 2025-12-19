import logging
from typing import Any

from PySide6.QtCore import QItemSelection, QPoint, Qt, Signal, Slot
from PySide6.QtWidgets import QMenu, QTreeView, QVBoxLayout
from shutterbug.core.app_controller import AppController
from shutterbug.core.models import (
    OutlinerModel,
    FITSModel,
    StarIdentity,
    GraphDataModel,
)
from shutterbug.gui.views.registry import register_view
from .base_view import BaseView
from shutterbug.gui.commands import (
    RemoveStarCommand,
    RemoveImageCommand,
    RemoveGraphCommand,
)


@register_view()
class Outliner(BaseView):

    name = "Outliner"
    object_selected = Signal(object)

    mapping = {
        FITSModel: RemoveImageCommand,
        StarIdentity: RemoveStarCommand,
        GraphDataModel: RemoveGraphCommand,
    }

    def __init__(self, controller: AppController, parent=None):
        super().__init__(controller, parent)
        self.setObjectName("outliner")

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
        self.item_view.setAlternatingRowColors(True)
        layout.addWidget(self.item_view)

        # Set up right-click context menu
        self.item_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.item_view.customContextMenuRequested.connect(self.show_context_menu)

        self.item_view.selectionModel().selectionChanged.connect(
            self._on_selection_changed
        )

        logging.debug("Outliner initialized")

    def on_activated(self):
        """handle creation of outliner"""
        self.item_view.selectionModel().selectionChanged.connect(
            self._on_selection_changed
        )

        # Creation subscriptions
        self.subscribe("image.created", lambda evt: self.model.add_image(evt.data))
        self.subscribe("graph.created", lambda evt: self.model.add_graph(evt.data))
        self.subscribe("star.created", lambda evt: self.model.add_star(evt.data))
        # Destruction subscriptions
        self.subscribe("image.removed", lambda evt: self.model.remove_image(evt.data))
        self.subscribe("graph.removed", lambda evt: self.model.remove_graph(evt.data))
        self.subscribe("star.removed", lambda evt: self.model.remove_star(evt.data))

        for star in self.controller.stars.all:
            self.model.add_star(star)
        for image in self.controller.images.all:
            self.model.add_image(image)
        for graph in self.controller.graphs.all:
            self.model.add_graph(graph)

    def on_deactivated(self):
        """Handle destruction of outliner"""
        super().on_deactivated()
        self.item_view.selectionModel().selectionChanged.disconnect(
            self._on_selection_changed
        )

    @Slot(QItemSelection, QItemSelection)
    def _on_selection_changed(self, selected: QItemSelection, _: QItemSelection):
        """Emits the selected data object from outliner click"""
        # Get from internal list
        s = selected.indexes()[0]
        # Data stored in item
        data = s.data(Qt.ItemDataRole.UserRole)
        if data is None:
            return  # No need to do anything
        self.controller.selections.select(data)

    @Slot(QPoint)
    def show_context_menu(self, pos: QPoint):
        """Displays context menu for right-clicked item in file list"""
        selection = self.item_view.selectionModel()
        data = selection.currentIndex().data(Qt.ItemDataRole.UserRole)
        menu = QMenu()

        delete_action = menu.addAction("Delete")
        delete_action.triggered.connect(lambda: self._remove_item(data))

        menu.exec(self.item_view.mapToGlobal(pos))

    def _remove_item(self, item: Any):
        """Removes item from system"""
        cmd = self.mapping.get(type(item))
        if cmd:
            self.controller._undo_stack.push(cmd(item, self.controller))
