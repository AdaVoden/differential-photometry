import sys
import logging

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from shutterbug.gui.main_window import MainWindow

from qt_material import apply_stylesheet


def main():
    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)
    window = MainWindow()
    # qt material theme
    apply_stylesheet(app, theme="dark_purple.xml")

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
