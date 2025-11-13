from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QVBoxLayout, QWidget
from shutterbug.core.models import GraphDataModel


class GraphViewer(QWidget):
    """Viewer for star data in spreadsheet format"""

    def __init__(self):
        super().__init__()
        # Layout settings
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # Graph settings
        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.ax = self.figure.add_subplot(111)

    def display(self, graph_data: GraphDataModel):
        """Displays input graph"""

        xs = graph_data.get_xs()
        ys = graph_data.get_ys()
        err = graph_data.get_error()

        self.ax.clear()
        self.ax.errorbar(xs, ys, yerr=err, fmt="o", ecolor="black", capsize=3)
        self.ax.invert_yaxis()
        self.ax.set_xlabel(graph_data.x_label or "")
        self.ax.set_ylabel(graph_data.y_label or "")
        self.ax.set_xlim(graph_data.xlim)
        self.ax.set_ylim(graph_data.ylim)
        self.ax.set_title(graph_data.title or "")
        self.ax.grid(True)
        self.canvas.draw_idle()
