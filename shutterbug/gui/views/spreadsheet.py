from __future__ import annotations

from typing import TYPE_CHECKING, Any, List

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController


import logging
from shutterbug.core.events import Event
from PySide6.QtWidgets import QVBoxLayout, QWidget, QTableView, QHeaderView
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtCore import Slot, Qt

from shutterbug.gui.adapters.tabular_data_interface import TabularDataInterface


class SpreadsheetViewer(QWidget):
    """Viewer for star data in spreadsheet format"""

    def __init__(self, controller: AppController):
        super().__init__()
        # Default variables
        self.adapter: TabularDataInterface | None = None
        self.controller = controller
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

        # Handle signals
        controller.on("adapter.selected", self.set_adapter)

        logging.debug("Spreadsheet viewer initialized")

    def _row_from_id(self, id: str) -> int | None:
        """Finds index associated with id"""
        row = self.model.findItems(id, column=0)
        if row:
            idx = self.model.indexFromItem(row[0])
            return idx.row()
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

    @Slot(Event)
    def set_adapter(self, event: Event):
        """Sets the data adapter for the spreadsheet"""
        adapter = event.data
        if self.adapter != adapter:
            if self.adapter is not None:
                logging.debug(f"Removing adapter {type(adapter).__name__}")
                signals = self.adapter.signals
                signals.item_added.disconnect(self._add_row)
                signals.item_removed.disconnect(self._remove_row)
                signals.item_updated.disconnect(self._refresh_row)

            logging.debug(f"Setting adapter to {type(adapter).__name__}")
            self.adapter = adapter
            signals = self.adapter.signals
            signals.item_added.connect(self._add_row)
            signals.item_removed.connect(self._remove_row)
            signals.item_updated.connect(self._refresh_row)

            self.refresh()
        else:
            logging.debug("Adapter failed to update in spreadsheet")

    @Slot(str, int, object)
    def _refresh_row(self, id: str, column: int, value: Any):
        """Updates all information in the row"""
        row = self._row_from_id(id)
        if row is None:
            return
        logging.debug(f"Refreshing row {row}, column {column} in spreadsheet")
        item = self.model.item(row, column)
        item.setText(value)

    @Slot(list)
    def _add_row(self, row: List[QStandardItem]):
        """Adds row to model"""
        self.model.appendRow(row)

    @Slot(str)
    def _remove_row(self, id: str):
        """Removes row from model"""
        row = self._row_from_id(id)
        if row is None:
            return
        logging.debug(f"Removing row {row} in spreadsheet")
        self.model.removeRow(row)
