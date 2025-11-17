import logging
from typing import List
from PySide6.QtWidgets import QVBoxLayout, QWidget, QTableView, QHeaderView
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtCore import QModelIndex, Slot, Qt

from shutterbug.core.managers.selection_manager import SelectionManager
from shutterbug.gui.adapters.tabular_data_interface import TabularDataInterface


class SpreadsheetViewer(QWidget):
    """Viewer for star data in spreadsheet format"""

    def __init__(self):
        super().__init__()
        # Default variables
        self.adapter: TabularDataInterface | None = None
        self.selection_manager = SelectionManager()

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
        self._clear_all()
        if self.adapter is None:
            return  # No work to do

        headers = self.adapter.get_column_headers()
        self.model.setHorizontalHeaderLabels(headers)

        data_rows = self.adapter.get_row_data()
        for row in data_rows:
            self.model.appendRow(row)

    def set_adapter(self, adapter: TabularDataInterface):
        """Sets the data adapter for the spreadsheet"""
        if self.adapter is not None:
            signals = self.adapter.signals
            signals.item_added.disconnect(self._add_row)
            signals.item_removed.disconnect(self._remove_row)
            signals.item_updated.disconnect(self._refresh_row)

        self.adapter = adapter
        signals = self.adapter.signals
        signals.item_added.connect(self._add_row)
        signals.item_removed.connect(self._remove_row)
        signals.item_updated.connect(self._refresh_row)

        self.refresh()

    @Slot(object)
    def _refresh_row(self, row: List[QStandardItem]):
        """Updates all information in the row"""
        id = row[0].data(Qt.ItemDataRole.UserRole)
        idx = self._idx_from_id(id)
        if idx is None:
            return
        cols = self.model.columnCount()
        for col in range(0, cols):
            self.model.setItem(idx.row(), col, row[col])

    @Slot(object)
    def _add_row(self, row: List[QStandardItem]):
        """Adds row to model"""
        self.model.appendRow(row)

    @Slot(object)
    def _remove_row(self, row: List[QStandardItem]):
        """Removes row from model"""
        id = row[0].data(Qt.ItemDataRole.UserRole)
        idx = self._idx_from_id(id)
        if idx is None:
            return
        self.model.removeRow(idx.row())
