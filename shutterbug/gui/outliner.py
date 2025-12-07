import logging
from shutterbug.core.events import Event

from PySide6.QtCore import QItemSelection, QPoint, Qt, Signal, Slot
from PySide6.QtWidgets import QMenu, QTreeView, QVBoxLayout, QWidget
from shutterbug.core.app_controller import AppController
from shutterbug.core.models import OutlinerModel
from shutterbug.core.models.fits_model import FITSModel


class Outliner(QWidget):

    object_selected = Signal(object)

    def __init__(self, controller: AppController):
        super().__init__()
        self.setObjectName("outliner")

        # Keep
        self.controller = controller

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
        controller.on("image.created", lambda evt: self.model.add_image(evt.data))
        controller.on("graph.created", lambda evt: self.model.add_graph(evt.data))
        controller.on("star.created", lambda evt: self.model.add_star(evt.data))

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
        self.controller.selections.set_selected_object(data)

    @Slot(QPoint)
    def show_context_menu(self, pos: QPoint):
        """Displays context menu for right-clicked item in file list"""
        selection = self.item_view.selectionModel().selection()
        menu = QMenu()

        delete_action = menu.addAction("Delete")

        menu.exec(self.item_view.mapToGlobal(pos))
