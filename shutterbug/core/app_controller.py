import logging
from pathlib import Path

from shutterbug.core.events.change_event import Event
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QUndoStack
from shutterbug.gui.adapters import (
    FITSModelAdapter,
    StarIdentityAdapter,
)
from shutterbug.gui.adapters.adapter_registry import AdapterRegistry
from shutterbug.gui.managers.icon_manager import IconManager
from shutterbug.gui.managers.theme_manager import ThemeManager

from .managers import (
    FileManager,
    GraphManager,
    ImageManager,
    SelectionManager,
    StarCatalog,
)
from .models import FITSModel, StarIdentity
from shutterbug.gui.managers import MarkerManager

ADAPTERS = [(FITSModel, FITSModelAdapter), (StarIdentity, StarIdentityAdapter)]


class AppController(QObject):

    change_event = Signal(Event)

    def __init__(self):
        super().__init__()

        # Instantiate managers

        # Core managers
        self.files = FileManager(self)
        self.images = ImageManager(self)
        self.stars = StarCatalog(self)
        self.graphs = GraphManager(self)
        self.adapters = AdapterRegistry(self)
        self.selections = SelectionManager(self)
        # GUI managers
        self.markers = MarkerManager(self)
        self.icons = IconManager(self)
        self.themes = ThemeManager(self)

        # Undo stack
        self._undo_stack = QUndoStack()

        self.register_adapters()
        self.themes.apply_theme()

        logging.debug("App Controller initialized")

    def dispatch(self, evt: Event):
        """Dispatches events"""
        logging.debug(f"EVENT: {evt.key}")
        self.change_event.emit(evt)

    def on(self, pattern: str, callback):
        """Sets up callback for event, if match"""

        def listener(evt):
            if self._match(evt.key, pattern):
                callback(evt)

        self.change_event.connect(listener)
        return listener

    def _match(self, key, pattern):
        """Matches event domain and action to pattern"""
        if pattern.endswith(".*"):
            return key.startswith(pattern[:-2])
        return key == pattern

    @Slot()
    def on_redo(self):
        if self._undo_stack.canRedo():
            self._undo_stack.redo()

    @Slot()
    def on_undo(self):
        if self._undo_stack.canUndo():
            self._undo_stack.undo()

    def register_adapters(self):
        registry = self.adapters
        for cls, adapter in ADAPTERS:
            registry.register_adapter(cls, adapter)
            logging.debug(f"Registered {cls.__name__} adapter")

    @property
    def resources(self):
        """Returns resources folder"""
        return Path(__file__).resolve().parent.parent / "resources"
