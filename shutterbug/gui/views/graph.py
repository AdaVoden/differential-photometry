from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shutterbug.gui.main_window import MainWindow

import logging
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QVBoxLayout, QWidget
from shutterbug.core.models import GraphDataModel


class GraphViewer(QWidget):
    """Viewer for star data in spreadsheet format"""

    def __init__(self, main_window: MainWindow):
        super().__init__()
        # Layout settings
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.graph = None
        # Graph settings
        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        self.ax = None
        layout.addWidget(self.canvas)

        main_window.graph_selected.connect(self._on_active_graph_change)

    def _clear(self):
        """Clears active graph and axes object"""
        if self.ax is None:
            return  # No work to do

        self.ax.clear()
        self.figure.clear()
        self.ax = None

    @Slot(GraphDataModel)
    def _on_active_graph_change(self, graph_data: GraphDataModel | None):
        if graph_data is None:
            logging.debug(f"Graph viewer clearing graph, no graph selected")
            self._clear()
            self.graph = None
            return
        logging.debug(f"Graph updated in graphing viewer")
        self.graph = graph_data
        self._clear()
        self.display()

    def display(self):
        """Displays input graph"""
        graph_data = self.graph
        if graph_data is None:
            return

        xs = graph_data.get_xs()
        ys = graph_data.get_ys()
        err = graph_data.get_error()

        self.ax = self.figure.add_subplot(111)
        self.ax.errorbar(xs, ys, yerr=err, fmt="o", ecolor="black", capsize=3)
        self.ax.invert_yaxis()
        self.ax.set_xlabel(graph_data.x_label or "")
        self.ax.set_ylabel(graph_data.y_label or "")
        self.ax.set_xlim(graph_data.xlim)
        self.ax.set_ylim(graph_data.ylim)
        self.ax.set_title(graph_data.title or "")
        self.ax.grid(True)
        self.canvas.draw_idle()
