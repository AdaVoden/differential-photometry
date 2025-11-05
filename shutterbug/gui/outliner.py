import logging

from shutterbug.gui.image_manager import ImageManager
from shutterbug.gui.image_data import FITSImage
from shutterbug.gui.commands.main_commands import (
    RemoveImagesCommand,
    SelectFileCommand,
)

from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QMenu
from PySide6.QtCore import Signal, Slot, Qt, QPoint
from PySide6.QtGui import QUndoStack

from typing import List


class Outliner(QWidget):

    remove_item_requested = Signal(str)  # Signal emitted when an item is deleted

    def __init__(self, undo_stack: QUndoStack, image_manager: ImageManager):
        super().__init__()
        self.setObjectName("outliner")

        self._undo_stack = undo_stack

        # Keep track of images
        self.image_manager = image_manager

        self.selected_item = None
        self.loaded_items: List[str] = []  # List to keep track of loaded items

        # Set layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        # Remove layout styling
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Create a file list and connect it here
        self.file_list = QListWidget()
        layout.addWidget(self.file_list)

        # Set up right-click context menu
        self.file_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)

        self.file_list.itemClicked.connect(self._on_item_clicked)

        # Image manager signals
        self.image_manager.active_image_changed.connect(self._on_active_image_changed)
        self.image_manager.images_added.connect(self._on_images_added)
        self.image_manager.images_removed.connect(self._on_images_removed)

        logging.debug("Outliner initialized")

    @Slot(FITSImage)
    def _on_active_image_changed(self, image: FITSImage | None):
        """Handles active image being changed"""
        if image:
            self.select_item(image.filename)

    @Slot(FITSImage)
    def _on_images_removed(self, images: List[FITSImage]):
        """Handles images being removed from manager"""
        for image in images:
            item = self.get_item(image.filename)
            if item:
                self.remove_item(item)

    @Slot(FITSImage)
    def _on_images_added(self, images: List[FITSImage]):
        """Handles images being added to manager"""
        for image in images:
            self.add_item(image.filename)

    @Slot(QPoint)
    def show_context_menu(self, pos: QPoint):
        """Displays context menu for right-clicked item in file list"""
        clicked_item = self.file_list.itemAt(pos)
        if clicked_item:
            menu = QMenu()

            delete_action = menu.addAction("Delete")
            delete_action.triggered.connect(self._on_delete_item)

            menu.exec(self.file_list.mapToGlobal(pos))

    @Slot(str)
    def _on_delete_item(self, item_name: str):
        """Create delete command of item"""
        self._undo_stack.push(
            RemoveImagesCommand(
                [item_name],
                self.image_manager,
            )
        )

    @Slot(QListWidgetItem)
    def _on_item_clicked(self, item: QListWidgetItem):
        """Handle item click events"""
        logging.debug(f"Item clicked: {item.text()}")
        image = self.image_manager.get_image(item.text())
        self._undo_stack.push(SelectFileCommand(image, self.image_manager))

    @Slot(str)
    def add_item(self, item_name: str):
        """Add an item to the outliner"""
        self.file_list.addItem(item_name)
        self.loaded_items.append(item_name)

    @Slot(str)
    def select_item(self, item_name: str | None):
        """Selects an item in the outliner"""
        if item_name is None:
            logging.debug("Clearing Outliner selection")
            self.file_list.clearSelection()
            self.selected_item = None
            return

        for item in self.file_list.findItems(item_name, Qt.MatchFlag.MatchExactly):
            if item.text() == item_name:
                logging.debug(f"Selecting item {item_name} in Outliner")
                self.file_list.setCurrentItem(item)
                self.selected_item = item
                return  # No more work to do

    @Slot(QListWidgetItem)
    def remove_item(self, item: QListWidgetItem):
        """Remove an item from the outliner"""
        logging.debug(f"Removing item: {item.text()}")
        row = self.file_list.row(item)
        self.file_list.takeItem(row)

    def get_item(self, item_name: str) -> QListWidgetItem | None:
        """Get item from outliner by item name"""
        for item in self.file_list.findItems(item_name, Qt.MatchFlag.MatchExactly):
            if item.text() == item_name:
                return item
        return None

    def get_state(self):
        return {"items": self.loaded_items, "selected_item": self.selected_item}

    def set_state(self, state):
        for item in state["items"]:
            self.add_item(item)
        self.selected_item = state["selected_item"]
        selected_item = self.file_list.findItems(
            self.selected_item, Qt.MatchFlag.MatchExactly
        )[0]
        self.file_list.setCurrentItem(selected_item)
        self._on_item_clicked(selected_item)
