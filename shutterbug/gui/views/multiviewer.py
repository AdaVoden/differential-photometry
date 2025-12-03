from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

import logging
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QStackedWidget,
)
from PySide6.QtCore import Signal, Slot

from shutterbug.gui.tools.base_tool import BaseTool
from shutterbug.gui.views import ImageViewer, GraphViewer, SpreadsheetViewer


class MultiViewer(QWidget):
    """Viewer that can switch between multiple modes"""

    propagation_requested = Signal()
    batch_requested = Signal()
    tool_changed = Signal(BaseTool)
    tool_settings_changed = Signal(QWidget)

    def __init__(self, controller: AppController):
        super().__init__()
        self.setObjectName("multiviewer")

        # Top bar
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["Image Viewer", "Graph Viewer", "Spreadsheet"])

        top_bar = QHBoxLayout()
        top_bar.addWidget(self.mode_selector)
        top_bar.addStretch()
        top_bar.setObjectName("topbar")

        # Stacked views
        self.image_viewer = ImageViewer(controller)
        self.graph_viewer = GraphViewer(controller)  # Placeholder
        self.table_viewer = SpreadsheetViewer(controller)

        self.stack = QStackedWidget()
        self.stack.addWidget(self.image_viewer)
        self.stack.addWidget(self.graph_viewer)
        self.stack.addWidget(self.table_viewer)

        # Layout
        layout = QVBoxLayout()
        layout.addLayout(top_bar)
        layout.addWidget(self.stack)
        self.setLayout(layout)

        # Remove styling from layouts
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Connections
        self.mode_selector.currentIndexChanged.connect(self.change_mode)
        self.image_viewer.propagation_requested.connect(self.propagation_requested)
        self.image_viewer.batch_requested.connect(self.batch_requested)
        self.image_viewer.tool_changed.connect(self.tool_changed)
        self.image_viewer.tool_settings_changed.connect(self.tool_settings_changed)

        logging.debug("Multiviewer intialized")

    @Slot(int)
    def change_mode(self, index: int):
        self.stack.setCurrentIndex(index)
