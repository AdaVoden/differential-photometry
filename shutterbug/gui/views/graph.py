from __future__ import annotations

from typing import TYPE_CHECKING

from matplotlib.backends.backend_qt import NavigationToolbar2QT

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

import logging
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QVBoxLayout

from shutterbug.core.events.change_event import Event
from .base_view import BaseView
from .registry import register_view

from astropy.time import Time


@register_view()
class GraphViewer(BaseView):
    """Viewer for star data in spreadsheet format"""

    name = "Graph Viewer"

    def __init__(self, controller: AppController, parent=None):
        super().__init__(controller, parent)
        # Layout settings
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.graph = controller.selections.graph
        # Graph settings
        self.figure = Figure(figsize=(5, 4))
        self.figure.tight_layout()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        self.ax = None
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        if self.graph:
            self.display()

    def on_activated(self):
        """On the graph viewer's initial activation"""
        self.subscribe("graph.selected", self._on_graph_selected)
        self.subscribe("graph.updated.*", self._on_active_graph_change)
        self.graph = self.controller.selections.graph
        if self.graph:
            self.display()

    def _clear(self):
        """Clears active graph and axes object"""
        if self.ax is None:
            return  # No work to do

        self.ax.clear()
        self.figure.clear()
        self.ax = None

    @Slot(Event)
    def _on_graph_selected(self, event: Event):
        graph = event.data
        if graph is None:
            logging.debug(f"Graph viewer clearing graph, no graph selected")
            self._clear()
            self.graph = None
            return
        self.graph = graph
        self._clear()
        self.display()

    @Slot(Event)
    def _on_active_graph_change(self, event: Event):
        graph_data = event.data
        if graph_data is None:
            logging.debug(f"Graph viewer clearing graph, no graph selected")
            self._clear()
            self.graph = None
            return
        if self.graph == graph_data:
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
        xs = Time(xs, format="jd").to_datetime()
        err = graph_data.get_error()

        self.ax = self.figure.add_subplot(111)
        self.ax.errorbar(xs, ys, yerr=err, fmt="o", ecolor="black", capsize=3)
        self.ax.invert_yaxis()
        self.ax.set_xlabel(graph_data.x_label or "")
        self.ax.set_ylabel(graph_data.y_label or "")
        self.ax.set_xlim(graph_data.xlim)
        self.ax.set_ylim(graph_data.ylim)
        self.ax.set_title(graph_data.title or "")
        # prettification of x-axis
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        self.ax.tick_params(axis="x", labelrotation=45)
        self.ax.grid(True)
        self.ax.yaxis.set_inverted(True)
        self.canvas.draw_idle()
