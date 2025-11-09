from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class SpreadsheetViewer(QWidget):
    """Viewer for star data in spreadsheet format"""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Spreadsheet Viewer Placeholder"))
        self.setLayout(layout)
