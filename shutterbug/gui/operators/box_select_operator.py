from __future__ import annotations
from typing import TYPE_CHECKING

from shutterbug.gui.tools.box_select_settings import BoxSelectOperatorSettingsWidget

if TYPE_CHECKING:
    from shutterbug.gui.views.image import ImageViewer

from PySide6.QtCore import QRect, QSize, QTimer, Slot
from PySide6.QtGui import QMouseEvent, QPen, QColor
from PySide6.QtWidgets import QRubberBand
from shutterbug.gui.commands.star_commands import AddMeasurementsCommand
from shutterbug.gui.operators.base_operator import BaseOperator
from shutterbug.gui.operators.operator_parameters import BoxSelectParameters


class BoxSelectOperator(BaseOperator):

    def __init__(self, viewer: ImageViewer, params: BoxSelectParameters):
        super().__init__(viewer)
        # Parameters live here
        self.params = params
        self.params.changed.connect(self._on_params_changed)

        # Initial variables
        self.start_pos = None
        self.end_pos = None
        self.rubber = None
        self.preview_items = []

        # Debounce timer
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self._update_preview)

    def create_settings_widget(self) -> BoxSelectOperatorSettingsWidget:
        return BoxSelectOperatorSettingsWidget(self.params)

    def start(self, event: QMouseEvent):
        """Begins selection box at point of click"""
        self.start_pos = event.pos()
        self.rubber = QRubberBand(QRubberBand.Shape.Rectangle, self.viewer)
        self.rubber.setGeometry(QRect(event.pos(), QSize()))
        self.rubber.show()

    def update(self, event: QMouseEvent):
        """Updates selection box on mouse move"""
        if not self.active:
            return
        self.end_pos = event.pos()
        if self.start_pos and self.end_pos:
            rect = QRect(self.start_pos, self.end_pos).normalized()
            if self.rubber:
                self.rubber.setGeometry(rect)

            # Compute scene rect
            self.scene_rect = self.viewer.viewport_rect_to_scene(rect)
            self.debounce_timer.stop()
            self.debounce_timer.start(42)  # ~24 fps

    def build_command(self):
        """Builds command that adds star measurements to project"""
        if not self.rubber:
            return  # No work to do

        scene_rect = self.viewer.viewport_rect_to_scene(self.rubber.geometry())
        stars = self._find_stars_in(scene_rect)

        if not stars or self.viewer.current_image is None:
            return None  # Things have gone wrong

        return AddMeasurementsCommand(stars, self.viewer.current_image)

    def cleanup_preview(self):
        """Cleans preview"""
        if self.rubber:
            self.rubber.deleteLater()
            self.rubber.hide()
            self.rubber = None
        # Clear old preview items
        for item in self.preview_items:
            item.scene().removeItem(item)
        self.preview_items.clear()

    def _update_preview(self):
        """Updates preview of command"""
        # Clear old preview
        for item in self.preview_items:
            item.scene().removeItem(item)

        self.preview_items.clear()

        # Query stars using threshold
        if not self.rubber:
            return  # Something broke
        stars = self._find_stars_in(self.scene_rect)

        if not stars or self.viewer.current_image is None:
            return None

        # Build the preview
        for star in stars:
            pen = QPen(QColor("cyan"))
            pen.setWidth(2)

            circle = self.viewer.scene().addEllipse(
                star["xcentroid"] - 20, star["ycentroid"] - 20, 40, 40, pen
            )
            self.preview_items.append(circle)

    def _find_stars_in(self, scene_rect: QRect):
        """Finds stars in a rectangle"""
        upper_left = scene_rect.topLeft()
        bottom_right = scene_rect.bottomRight()

        image_manager = self.viewer.image_manager
        centroids = image_manager.find_centroids_from_points(
            upper_left, bottom_right, threshold=self.params.threshold
        )

        return centroids

    @Slot()
    def _on_params_changed(self):
        """Handles parameters changing in Box Selection"""
        if self.active:
            self._update_preview()
