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
        data = QStandardItem(graph_model.label)
        data.setData(graph_model, Qt.ItemDataRole.UserRole)
        self.graphs_item.appendRow(data)

    def add_star(self, star_model: StarIdentity):
        data = QStandardItem(star_model.id)
        data.setData(star_model, Qt.ItemDataRole.UserRole)
        self.stars_item.appendRow(data)

    def _find_in_item(self, text: str, item: QStandardItem):
        for row in range(item.rowCount()):
            i = item.child(row)
            if i.text() == text:
                return row
        return -1

    def remove_image(self, fits_model: FITSModel):
        row = self._find_in_item(fits_model.filename, self.images_item)
        if row >= 0:
            self.images_item.takeChild(row)

    def remove_graph(self, graph_model: GraphDataModel):
        row = self._find_in_item(graph_model.label, self.graphs_item)
        if row >= 0:
            self.graphs_item.takeChild(row)

    def remove_star(self, star_model: StarIdentity):
        row = self._find_in_item(star_model.id, self.stars_item)
        if row >= 0:
            self.stars_item.takeChild(row)
