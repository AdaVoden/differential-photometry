import sys
import logging

from PySide6.QtWidgets import QApplication
from shutterbug.core.app_controller import AppController
from shutterbug.gui.main_window import MainWindow


def main():
    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)
    controller = AppController()
    window = MainWindow(controller)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
