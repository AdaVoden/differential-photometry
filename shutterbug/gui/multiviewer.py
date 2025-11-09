from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QStackedWidget,
)
from PySide6.QtGui import QUndoStack
from PySide6.QtCore import Signal, Slot

from .viewer import Viewer


class MultiViewer(QWidget):
    """Viewer that can switch between multiple modes"""

    propagation_requested = Signal()
    batch_requested = Signal()

    def __init__(self, undo_stack: QUndoStack):
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
        self.image_viewer = Viewer(undo_stack)
        self.graph_viewer = QWidget()  # Placeholder
        self.table_viewer = QWidget()

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

    @Slot(int)
    def change_mode(self, index: int):
        self.stack.setCurrentIndex(index)
