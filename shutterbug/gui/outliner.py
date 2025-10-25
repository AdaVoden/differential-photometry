import logging
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget
from PySide6.QtCore import Signal, Slot


class Outliner(QWidget):

    item_selected = Signal(object)  # Signal emitted when an item is selected

    def __init__(self):
        super().__init__()

        # Set a minimum height for the outliner
        self.setMinimumHeight(200)
        # Set layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create a file list and connect it here
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.file_list)

        self.loaded_items = []  # Dictionary to keep track of loaded items

        logging.debug("Outliner initialized")

    def add_item(self, item_name):
        """Add an item to the outliner"""
        self.file_list.addItem(item_name)
        self.loaded_items.append(item_name)

    @Slot()
    def on_item_clicked(self, item):
        """Handle item click events"""
        logging.debug(f"Item clicked: {item.text()}")
        # Emit signal
        self.item_selected.emit(item.text())
