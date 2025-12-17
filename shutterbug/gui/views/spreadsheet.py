from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController


import logging
from shutterbug.core.events import Event
from PySide6.QtWidgets import (
    QComboBox,
    QMenu,
    QVBoxLayout,
    QTableView,
    QHeaderView,
    QWidget,
)
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtCore import Slot

from shutterbug.gui.adapters.tabular_data_interface import TabularDataInterface
from shutterbug.gui.views.registry import register_view
from .base_view import BaseView


@register_view()
class SpreadsheetViewer(BaseView):
    """Viewer for star data in spreadsheet format"""

    name = "Spreadsheet Viewer"

    def __init__(self, controller: AppController, parent=None):
        super().__init__(controller, parent)
        # Default variables
        self.adapter: Optional[TabularDataInterface] = None
        self.view_types = []
        self.selected_type = None
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

    def on_activated(self):
        """Handles spreadsheet viewer's first time activation"""
        self.subscribe("adapter.selected", self._on_adapter_selected)
        adapter = self.controller.selections.adapter
        self.set_adapter(adapter)

    def create_header_actions(self) -> List[QMenu | QWidget]:
        self.views = QComboBox()
        for k, v in self.controller.adapters._registry.items():
            self.views.addItem(v.name)
            self.view_types.append(k)

        self.views.currentIndexChanged.connect(self._on_view_selected)

        return [self.views]

    @Slot(int)
    def _on_view_selected(self, index: int):
        """Handles Spreadsheet view being selected"""
        self.selected_type = self.views.itemText(index)
        selected_item = getattr(self.controller.selections, self.view_types[index].type)
        if selected_item:
            adapter = self.controller.adapters.get_adapter_for(selected_item)
            self.set_adapter(adapter)
        else:
            self.set_adapter(None)

    @Slot(Event)
    def _on_adapter_selected(self, event: Event):
        """Handles adapter of same type being selected"""
        adapter = event.data
        if not self.selected_type:
            return
        if adapter is not None and self.selected_type == adapter.name:
            if self.adapter != adapter:
                self.set_adapter(adapter)
            else:
                self.refresh()

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

    def set_adapter(self, adapter: TabularDataInterface | None):
        """Sets the data adapter for the spreadsheet"""
        if self.adapter is not None:
            logging.debug(f"Removing adapter {type(adapter).__name__}")
            signals = self.adapter.signals
            signals.item_added.disconnect(self._add_row)
            signals.item_removed.disconnect(self._remove_row)
            signals.item_updated.disconnect(self._refresh_row)

        logging.debug(f"Setting adapter to {type(adapter).__name__}")
        self.adapter = adapter
        if adapter:
            signals = adapter.signals
            signals.item_added.connect(self._add_row)
            signals.item_removed.connect(self._remove_row)
            signals.item_updated.connect(self._refresh_row)

        self.refresh()

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
