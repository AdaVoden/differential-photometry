from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel

from shutterbug.core.models import FITSModel, GraphDataModel, StarIdentity


class OutlinerModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self.images_item = QStandardItem("Images")
        self.graphs_item = QStandardItem("Graphs")
        self.stars_item = QStandardItem("Stars")

        self.appendRow(self.images_item)
        self.appendRow(self.graphs_item)
        self.appendRow(self.stars_item)

    def add_image(self, fits_model: FITSModel):
        data = QStandardItem(fits_model.filename)
        data.setData(fits_model, Qt.ItemDataRole.UserRole)
        self.images_item.appendRow(data)

    def add_graph(self, graph_model: GraphDataModel):
        pass

    def add_star(self, star_model: StarIdentity):
        data = QStandardItem(star_model.id)
        data.setData(star_model, Qt.ItemDataRole.UserRole)
        self.stars_item.appendRow(data)
