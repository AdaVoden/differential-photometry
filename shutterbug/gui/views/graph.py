from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class GraphViewer(QWidget):
    """Viewer for star data in spreadsheet format"""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Graph Viewer Placeholder"))
        self.setLayout(layout)
