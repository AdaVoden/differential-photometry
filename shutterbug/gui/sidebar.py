from PySide6.QtWidgets import QWidget, QHBoxLayout

from shutterbug.gui.outliner import Outliner
from shutterbug.gui.tool_settings import Settings

class Sidebar(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Initialize sidebar components here

        layout = QHBoxLayout()
        # Outliner on top, Settings below
        self.outliner = Outliner(self)
        self.settings = Settings(self)  

        layout.addWidget(self.outliner)
        layout.addWidget(self.settings)
        self.setLayout(layout)
        self.setMaximumWidth(400) # set a maximum width for the sidebar
        