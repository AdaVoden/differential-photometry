from PySide6.QtWidgets import QWidget


class BaseSettings(QWidget):

    name = "Base Settings"

    def __init__(self, params):
        super().__init__()
        self.params = params
        self._build_ui()

    def _build_ui(self):
        pass
