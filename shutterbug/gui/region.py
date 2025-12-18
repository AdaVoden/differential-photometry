import logging
from typing import Optional
from PySide6.QtCore import Signal, Qt, Slot
from PySide6.QtWidgets import QSplitter, QVBoxLayout, QWidget

from shutterbug.gui.panel import Panel

from uuid import uuid4


class Region(QWidget):

    split_requested = Signal(Qt.Orientation)
    collapse_requested = Signal(object)  # Emitting itself

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
        self.panel.collapse_requested.connect(self.collapse)

        logging.debug(f"Region {self.uid} initialized with panel {panel.name}")

    @Slot(Qt.Orientation)
    def split(
        self,
        orientation: Qt.Orientation,
        left_stretch: Optional[int] = None,
        right_stretch: Optional[int] = None,
    ):
        """Splits region into child regions"""
        old_panel = self.panel
        # Remove old widget
        self.is_leaf = False
        self.panel = None
        self._clear_self()

        layout = self.layout()
        if not layout:
            return

        self.splitter = QSplitter(orientation)
        if old_panel:
            self.child_a = Region(Panel(old_panel.name, old_panel.controller, self))
            self.child_b = Region(Panel(old_panel.name, old_panel.controller, self))

            self.splitter.addWidget(self.child_a)
            self.splitter.addWidget(self.child_b)
            # Set up initial sizing
            if left_stretch and right_stretch:
                self.splitter.setStretchFactor(0, left_stretch)
                self.splitter.setStretchFactor(1, right_stretch)

            layout.addWidget(self.splitter)

            self.child_a.collapse_requested.connect(self.collapse)
            self.child_b.collapse_requested.connect(self.collapse)

    @Slot(object)
    def collapse(self, region: object = None):
        """Collapses regions together"""
        if self.is_leaf:
            # Leafs cannot collapse
            self.collapse_requested.emit(self)
            return self.panel
        # We're not a leaf, time to become one
        # Prevent loops
        self.child_a.collapse_requested.disconnect(self.collapse)
        self.child_b.collapse_requested.disconnect(self.collapse)
        # Which child is going to survive?

        panel_a = self.child_a.collapse()
        panel_b = self.child_b.collapse()

        if region is None:
            self.panel = panel_a
            self.child_b._del_widget()
            self.child_b.deleteLater()
        elif self.child_a == region:
            self.panel = panel_a
            self.child_b._del_widget()
            self.child_b.deleteLater()
        elif self.child_b == region:
            self.panel = panel_b
            self.child_a._del_widget()
            self.child_a.deleteLater()
        layout = self.layout()
        # Finish making a leaf!
        if layout and self.panel:
            layout.addWidget(self.panel)
            self.panel.split_requested.connect(self.split)
            self.panel.collapse_requested.connect(self.collapse)

        self.is_leaf = True
        if self.splitter:
            self.splitter.deleteLater()
        self.splitter = None

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

    def _clear_self(self):
        """Removes main widget from layout"""
        layout = self.layout()
        if layout:
            item = layout.takeAt(0).widget()
            if item:
                if isinstance(item, Panel):
                    item.view.on_deactivated()
                item.deleteLater()

    def _del_widget(self):
        """Removes current set splitter or panel"""
        self._clear_self()
