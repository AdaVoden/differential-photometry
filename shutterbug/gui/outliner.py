from PySide6.QtWidgets import QWidget

class Outliner(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set a minimum height for the outliner
        self.setMinimumHeight(200) 
        