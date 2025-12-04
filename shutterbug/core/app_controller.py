import logging

from shutterbug.core.events.change_event import Event
import shutterbug.core.utility.photometry as phot
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QUndoCommand, QUndoStack
from PySide6.QtWidgets import QWidget
from shutterbug.gui.adapters import (
    FITSModelAdapter,
    StarIdentityAdapter,
)
from shutterbug.gui.adapters.adapter_registry import AdapterRegistry
from shutterbug.gui.managers import ToolManager
from shutterbug.gui.operators.base_operator import BaseOperator
from shutterbug.gui.tools import BaseTool

from .managers import (
    GraphManager,
    ImageManager,
    SelectionManager,
    StarCatalog,
    StretchManager,
)
from .models import FITSModel, GraphDataModel, StarIdentity, StarMeasurement

ADAPTERS = [(FITSModel, FITSModelAdapter), (StarIdentity, StarIdentityAdapter)]


class AppController(QObject):

    # Tool signals
    active_tool_changed = Signal(BaseTool)
    tool_settings_changed = Signal(QWidget)
    operator_changed = Signal(BaseOperator)
    operator_finished = Signal(QUndoCommand)
    operator_cancelled = Signal()

    change_event = Signal(Event)

    def __init__(self):
        super().__init__()

        # Instantiate managers
        self.images = ImageManager(self)
        self.stars = StarCatalog(self)
        self.graphs = GraphManager(self)
        self.stretches = StretchManager(self)
        self.adapters = AdapterRegistry(self)
        self.selections = SelectionManager(self)
        self.tools = ToolManager(self)

        self.register_adapters()
        # Undo stack
        self._undo_stack = QUndoStack()

        # Handle tool signals
        self.tools.tool_changed.connect(self.active_tool_changed)
        self.tools.tool_settings_changed.connect(self.tool_settings_changed)
        self.tools.operator_changed.connect(self.operator_changed)
        self.tools.operator_finished.connect(self.operator_finished)
        self.tools.operator_cancelled.connect(self.operator_cancelled)

        self.tools.operator_finished.connect(self._on_operator_finished)

        logging.debug("App Controller initialized")

    def dispatch(self, evt: Event):
        """Dispatches generic events"""
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
        if pattern.endwith(".*"):
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

    @Slot()
    def process_all_images(self):
        """Generate light curve from all loaded images"""
        current_image = self.images.active_image

        if current_image is None:
            return  # No work required

        self.propagate_star_selection(current_image)
        for image in self.images.get_all_images():
            self.process_single_image(image)

    def process_single_image(self, image: FITSModel):
        """Process one image for differential photometry"""

        for measurement in self.stars.get_measurements_by_image(image.filename):
            phot.measure_star_magnitude(measurement, data=image.data)

    @Slot(FITSModel)
    def propagate_star_selection(self, image: FITSModel):
        """Propagates star selection across all images"""
        images = self.images
        stars = self.stars.get_measurements_by_image(image.filename)

        for img in images.get_all_images():
            if img != image:
                # Propagate to all other images, ignore target

                for star in stars:
                    star_data = images.find_nearest_centroid(img, star.x, star.y)

                    if star_data:
                        measurement = StarMeasurement(
                            x=star_data["xcentroid"],
                            y=star_data["ycentroid"],
                            time=img.observation_time,
                            image=img.filename,
                        )
                        self.stars.register_measurement(measurement)

    @Slot(str)
    def differential_image(self, image_name: str | None = None):
        """Calculates differential photometry on all measurements in image"""
        if image_name is None:
            if self.images.active_image is None:
                return  # No work to do
            image_name = self.images.active_image.filename

        measurements = self.stars.get_measurements_by_image(image_name)

        for m in measurements:
            # This could be a better algorithm
            other_ms = [n for n in measurements if n != m]
            phot.calculate_differential_magnitude(m, other_ms)

    @Slot()
    def differential_all(self):
        """Calculates differential photometry on all images' measurements"""
        for image in self.images.get_all_images():
            self.differential_image(image.filename)

    @Slot()
    def create_graph_from_selection(self):
        star = self.stars.active_star
        logging.debug("Graph creation called")
        if star is not None:
            graph = GraphDataModel.from_star(star)
            self.graphs.add_graph(graph)
            self.graphs.set_active_graph(graph)

    @Slot(QUndoCommand)
    def _on_operator_finished(self, cmd: QUndoCommand):
        self._undo_stack.push(cmd)

    def register_adapters(self):
        registry = self.adapters
        for cls, adapter in ADAPTERS:
            registry.register_adapter(cls, adapter)
            logging.debug(f"Registered {cls.__name__} adapter")
