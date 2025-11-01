import logging

from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QMenu
from PySide6.QtCore import Signal, Slot, Qt, QPoint

from typing import List


class Outliner(QWidget):

    item_selected = Signal(str)  # Signal emitted when an item is selected
    item_removed = Signal(str)  # Signal emitted when an item is deleted

    def __init__(self):
        super().__init__()
        self.selected_item = None
        self.loaded_items: List[str] = []  # Dictionary to keep track of loaded items

        # Set a minimum height for the outliner
        self.setMinimumHeight(200)
        # Set layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create a file list and connect it here
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.on_item_clicked)
        self.file_list.item
        layout.addWidget(self.file_list)

        # Set up right-click context menu
        self.file_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)

        logging.debug("Outliner initialized")

    @Slot(QPoint)
    def show_context_menu(self, pos: QPoint):
        """Displays context menu for right-clicked item in file list"""
        clicked_item = self.file_list.itemAt(pos)
        if clicked_item:
            menu = QMenu()

            delete_action = menu.addAction("Delete")
            delete_action.triggered.connect(lambda: self.remove_item(clicked_item))

            menu.exec(self.file_list.mapToGlobal(pos))

    def add_item(self, item_name: str):
        """Add an item to the outliner"""
        self.file_list.addItem(item_name)
        self.loaded_items.append(item_name)

    def select_item(self, item_name: str):
        """Selects an item in the outliner"""
        for item in self.file_list.findItems(item_name, Qt.MatchFlag.MatchExactly):
            if item.text() == item_name:
                self.file_list.setCurrentItem(item)
                return # No more work to do
        

    Slot(QListWidgetItem)
    def remove_item(self, item: QListWidgetItem):
        """Remove an item from the outliner"""
        logging.debug(f"Removing item: {item.text()}")
        row = self.file_list.row(item)
        removed = self.file_list.takeItem(row)

        self.item_removed.emit(removed.text())

    @Slot(QListWidgetItem)
    def on_item_clicked(self, item: QListWidgetItem):
        """Handle item click events"""
        logging.debug(f"Item clicked: {item.text()}")
        self.selected_item = item.text()
        # Emit signal
        self.item_selected.emit(item.text())

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
        self.on_item_clicked(selected_item)
