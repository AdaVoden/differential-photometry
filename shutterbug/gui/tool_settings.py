import logging
from PySide6.QtWidgets import QWidget


class Settings(QWidget):
    def __init__(self):
        super().__init__()

        logging.debug("Tool settings initialized")
