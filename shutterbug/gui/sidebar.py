from PySide6.QtWidgets import QWidget, QVBoxLayout

from shutterbug.gui.outliner import Outliner
from shutterbug.gui.tool_settings import Settings


class Sidebar(QWidget):

    def __init__(self):
        super().__init__()
        # Initialize sidebar components here

        layout = QVBoxLayout()
        # Outliner on top, Settings below
        self.outliner = Outliner()
        self.settings = Settings()

        layout.addWidget(self.outliner, stretch=1)
        layout.addWidget(self.settings, stretch=3)
        self.setLayout(layout)
        self.setMaximumWidth(400)  # set a maximum width for the sidebar
