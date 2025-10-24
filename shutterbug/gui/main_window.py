from PySide6.QtWidgets import QMainWindow, QHBoxLayout

from shutterbug.gui.sidebar import Sidebar
from shutterbug.gui.viewer import Viewer

class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Shutterbug")

        # Create sidebar and viewer
        self.sidebar = Sidebar()
        self.viewer = Viewer()


        main_layout = QHBoxLayout()
        main_layout.addWidget(self.viewer, stretch=3) # Viewer takes most space
        main_layout.addWidget(self.sidebar, stretch=1) # Sidebar on the right
