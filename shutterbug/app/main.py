import sys
import logging

from PySide6.QtWidgets import QApplication
from shutterbug.core.app_controller import AppController
from shutterbug.core.models import StarIdentity, FITSModel
from shutterbug.gui.adapters import (
    FITSModelAdapter,
    AdapterRegistry,
    StarIdentityAdapter,
)
from shutterbug.gui.main_window import MainWindow

from pathlib import Path

ADAPTERS = [(FITSModel, FITSModelAdapter), (StarIdentity, StarIdentityAdapter)]


def register_adapters():
    registry = AdapterRegistry()
    for cls, adapter in ADAPTERS:
        registry.register_adapter(cls, adapter)
        logging.debug(f"Registered {cls.__name__} adapter")


def load_stylesheet():
    qss_dir = Path(__file__).parent.parent / "resources" / "qss"

    stylesheets = [
        qss_dir / "base.qss",
        qss_dir / "controls.qss",
        qss_dir / "panels.qss",
    ]

    combined = ""
    for qss_file in stylesheets:
        with open(qss_file, "r") as f:
            combined += f.read() + "\n"

    return combined


def main():
    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)
    register_adapters()
    controller = AppController()
    window = MainWindow(controller)

    # Open and load qss file
    app.setStyleSheet(app.styleSheet() + "\n" + load_stylesheet())

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
