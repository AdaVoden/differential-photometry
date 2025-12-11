from PySide6.QtCore import QObject, Signal


class OperatorParameters(QObject):
    changed = Signal()


class BoxSelectParameters(OperatorParameters):
    threshold = 3.0


class PhotometryParameters(OperatorParameters):
    mode = "all"
    images = "single"
    aperture_radius = 10
    annulus_inner_radius = 15
    annulus_outer_radius = 20
    number_type = "float"
    decimal_places = 1
    buffer = 0.1  # Pixel
