import logging
from PySide6.QtWidgets import QVBoxLayout, QWidget, QTableView, QHeaderView
from PySide6.QtGui import QStandardItemModel
from PySide6.QtCore import QModelIndex

from shutterbug.gui.adapters.tabular_data_interface import TabularDataInterface


class SpreadsheetViewer(QWidget):
    """Viewer for star data in spreadsheet format"""

    def __init__(self):
        super().__init__()
        # Default variables

        # Layout without styling
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # Default model
        self.model = QStandardItemModel()

        # Table View
        self.table_view = QTableView()
        self.table_view.setModel(self.model)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        layout.addWidget(self.table_view)
        # Connections

        logging.debug("Spreadsheet viewer initialized")

    def _idx_from_id(self, id: str) -> QModelIndex | None:
        """Finds index associated with id"""
        row = self.model.findItems(id)
        if row:
            idx = self.model.indexFromItem(row[0])
            return idx
        return None

    def _clear_all(self):
        """Clears all items from model and view"""
        self.model.clear()

    def refresh(self):
        """Refreshes all data in spreadsheet"""
        pass

    def set_adapter(self, adapter: TabularDataInterface):
        """Sets the data adapter for the spreadsheet"""
        pass
