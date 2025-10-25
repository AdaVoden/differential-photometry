import sys
import logging

from PySide6.QtWidgets import QApplication
from shutterbug.gui.main_window import MainWindow


def main():
    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
