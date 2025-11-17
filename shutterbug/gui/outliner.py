import logging

from PySide6.QtCore import QItemSelection, QPoint, Qt, Signal, Slot
from PySide6.QtGui import QUndoStack
from PySide6.QtWidgets import QMenu, QTreeView, QVBoxLayout, QWidget
from shutterbug.core.managers import ImageManager, StarCatalog
from shutterbug.core.models import OutlinerModel


class Outliner(QWidget):

    object_selected = Signal(object)

    def __init__(self, undo_stack: QUndoStack):
        super().__init__()
        self.setObjectName("outliner")

        self._undo_stack = undo_stack

        # Keep track of images
        self.image_manager = ImageManager()  # singleton
        self.catalog = StarCatalog()

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

        logging.debug("Outliner initialized")

    @Slot(QItemSelection, QItemSelection)
    def _on_selection_changed(self, selected: QItemSelection, _: QItemSelection):
        """Emits the selected data object from outliner click"""
        # Get from internal list
        s = selected.indexes()[0]
        # Data stored in item
        data = s.data(Qt.ItemDataRole.UserRole)
        self.object_selected.emit(data)

    @Slot(QPoint)
    def show_context_menu(self, pos: QPoint):
        """Displays context menu for right-clicked item in file list"""
        selection = self.item_view.selectionModel().selection()
        menu = QMenu()

        delete_action = menu.addAction("Delete")

        menu.exec(self.item_view.mapToGlobal(pos))
