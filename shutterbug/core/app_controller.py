import logging

from shutterbug.core.events.change_event import Event
import shutterbug.core.utility.photometry as phot
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QUndoStack
from shutterbug.gui.adapters import (
    FITSModelAdapter,
    StarIdentityAdapter,
)
from shutterbug.gui.adapters.adapter_registry import AdapterRegistry

from .managers import (
    FileManager,
    GraphManager,
    ImageManager,
    SelectionManager,
    StarCatalog,
)
from .models import FITSModel, GraphDataModel, StarIdentity, StarMeasurement
from shutterbug.gui.managers import MarkerManager

ADAPTERS = [(FITSModel, FITSModelAdapter), (StarIdentity, StarIdentityAdapter)]


class AppController(QObject):

    change_event = Signal(Event)

    def __init__(self):
        super().__init__()

        # Instantiate managers
        self.files = FileManager(self)
        self.images = ImageManager(self)
        self.stars = StarCatalog(self)
        self.graphs = GraphManager(self)
        self.adapters = AdapterRegistry(self)
        self.selections = SelectionManager(self)
        self.markers = MarkerManager(self)

        # Undo stack
        self._undo_stack = QUndoStack()

        self.register_adapters()

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

    @Slot(FITSModel)
    def process_all_images(self, image: FITSModel):
        """Generate light curve from all loaded images"""

        self.propagate_star_selection(image)
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
                            controller=self,
                            x=star_data["xcentroid"],
                            y=star_data["ycentroid"],
                            time=img.observation_time,
                            image_id=img.filename,
                        )
                        self.stars.register_measurement(measurement)

    @Slot(str)
    def differential_image(self, image_name: str):
        """Calculates differential photometry on all measurements in image"""

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
            graph = GraphDataModel.from_star(self, star)
            self.graphs.add_graph(graph)

    def register_adapters(self):
        registry = self.adapters
        for cls, adapter in ADAPTERS:
            registry.register_adapter(cls, adapter)
            logging.debug(f"Registered {cls.__name__} adapter")
