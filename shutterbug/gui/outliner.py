import logging

from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget
from PySide6.QtCore import Signal, Slot, Qt

from typing import List


class Outliner(QWidget):

    item_selected = Signal(object)  # Signal emitted when an item is selected

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
        layout.addWidget(self.file_list)

        logging.debug("Outliner initialized")

    def add_item(self, item_name: str):
        """Add an item to the outliner"""
        self.file_list.addItem(item_name)
        self.loaded_items.append(item_name)

    def remove_item(self, item_name):
        """Remove an item from the outliner"""
        items = self.file_list.findItems(item_name, Qt.MatchFlag.MatchExactly)
        # I don't like this approach but QListWidget has no direct removeItem method
        for item in items:
            row = self.file_list.row(item)
            self.file_list.takeItem(row)
            self.loaded_items.remove(item_name)

    @Slot()
    def on_item_clicked(self, item):
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
