import logging
from typing import List

from PySide6.QtCore import QPoint, Qt, Slot, Signal
from PySide6.QtGui import QStandardItem, QUndoStack
from PySide6.QtWidgets import QMenu, QTreeView, QVBoxLayout, QWidget
from shutterbug.core.managers import ImageManager, StarCatalog
from shutterbug.core.models import OutlinerModel


class Outliner(QWidget):

    selection_changed = Signal(QStandardItem, QStandardItem)

    def __init__(self, undo_stack: QUndoStack):
        super().__init__()
        self.setObjectName("outliner")

        self._undo_stack = undo_stack

        # Keep track of images
        self.image_manager = ImageManager()  # singleton
        self.catalog = StarCatalog()

        self.selected_item = None
        self.loaded_items: List[str] = []  # List to keep track of loaded items

        # Set layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        # Remove layout styling
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Create a file list and connect it here
        self.item_view = QTreeView()
        self.model = OutlinerModel()
        self.item_view.setModel(self.model)
        self.item_view.alternatingRowColors()
        layout.addWidget(self.item_view)

        # Set up right-click context menu
        self.item_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.item_view.customContextMenuRequested.connect(self.show_context_menu)

        self.item_view.selectionModel().selectionChanged.connect(self.selection_changed)

        self.image_manager.images_added.connect(self.model.add_image)
        self.catalog.star_added.connect(self.model.add_star)

        logging.debug("Outliner initialized")

    @Slot(QPoint)
    def show_context_menu(self, pos: QPoint):
        """Displays context menu for right-clicked item in file list"""
        selection = self.item_view.selectionModel().selection()
        menu = QMenu()

        delete_action = menu.addAction("Delete")

        menu.exec(self.item_view.mapToGlobal(pos))
