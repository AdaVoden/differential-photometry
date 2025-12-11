from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController

from typing import List, Optional

from shutterbug.core.models import StarIdentity

from .base_observable import ObservableQObject
from .star_measurement import StarMeasurement
from uuid import uuid4


class GraphDataModel(ObservableQObject):

    type = "graph"

    def __init__(
        self,
        controller: AppController,
        label: str,
        measurements: List[StarMeasurement],
        title: Optional[str] = None,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        xlim: Optional[float] = None,
        ylim: Optional[float] = None,
    ):
        super().__init__(controller)
        self.uid = uuid4().hex
        self.label = label
        self.measurements = sorted(measurements, key=lambda m: m.time)
        self.title = self._define_field("title", title)
        self.x_label = self._define_field("x_label", x_label)
        self.y_label = self._define_field("y_label", y_label)
        self.xlim = self._define_field("xlim", xlim)
        self.ylim = self._define_field("ylim", ylim)

    def set_limits(self, xlim: Optional[float] = None, ylim: Optional[float] = None):
        """Sets limit of the graph"""
        self._xlim = xlim
        self._ylim = ylim
        self.updated.emit(self)

    def get_ys(self):
        """Gets all x-values of graph"""
        return [m.diff_mag for m in self.measurements if m.diff_mag]

    def get_xs(self):
        """Gets all y-values of graph"""
        return [m.time for m in self.measurements]

    def get_error(self):
        """Gets all error of graph"""
        return [m.diff_err for m in self.measurements if m.diff_err]

    @classmethod
    def from_star(cls, label: str, controller: AppController, star: StarIdentity):
        return cls(controller, label, measurements=list(star.measurements.values()))
