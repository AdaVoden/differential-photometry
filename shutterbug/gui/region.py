import logging
from PySide6.QtCore import Signal, Qt, Slot
from PySide6.QtWidgets import QSplitter, QVBoxLayout, QWidget

from shutterbug.gui.panel import Panel

from uuid import uuid4


class Region(QWidget):

    split_requested = Signal(Qt.Orientation)

    def __init__(self, panel: Panel, parent=None):
        super().__init__(parent)
        self.panel = panel
        self.is_leaf = True
        self.splitter = None
        self.uid = uuid4().hex

        # Layout setup
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        layout.addWidget(self.panel)

        # Layout styling
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Set up signals
        self.panel.split_requested.connect(self.split)

        logging.debug(f"Region {self.uid} initialized with panel {panel.name}")

    @Slot(Qt.Orientation)
    def split(self, orientation: Qt.Orientation):
        """Splits region into child regions"""
        old_panel = self.panel
        self.is_leaf = False
        self.panel = None

        # Remove old widget from layout
        self._del_widget()

        layout = self.layout()
        if not layout:
            return

        self.splitter = QSplitter(orientation)
        if old_panel:
            self.child_a = Region(Panel(old_panel.name, old_panel.controller, self))
            self.child_b = Region(Panel(old_panel.name, old_panel.controller, self))

            self.splitter.addWidget(self.child_a)
            self.splitter.addWidget(self.child_b)

            layout.addWidget(self.splitter)

    def collapse(self, region):
        """Collapses regions together"""
        pass

    def set_panel(self, panel: Panel):
        """Sets the current panel"""
        if self.is_leaf:
            # Clear up signals
            if self.panel:
                self.panel.split_requested.disconnect(self.split)
            # Set up new panel and remove old
            self.panel = panel
            self._del_widget()
            layout = self.layout()
            if layout:
                layout.addWidget(self.panel)
            logging.debug(f"Region {self.uid} set to panel {panel.name}")
            return True
        else:
            logging.error(
                f"Attempted to set Region {self.uid} to panel {panel.name}, but is not a leaf"
            )
            return False

    def _del_widget(self):
        """Removes current set splitter or panel"""
        layout = self.layout()
        if layout:
            item = layout.takeAt(0).widget()

            if item:
                if isinstance(item, Panel):
                    item.view.on_deactivated()
                item.deleteLater()
                del item
