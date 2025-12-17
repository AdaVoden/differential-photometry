from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shutterbug.gui.views.image import ImageViewer
    from shutterbug.core.app_controller import AppController

from shutterbug.gui.tools.box_select_settings import BoxSelectOperatorSettingsWidget

from PySide6.QtCore import QRect, QSize, QTimer, Slot, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QRubberBand
from shutterbug.gui.commands.star_commands import AddMeasurementsCommand
from shutterbug.gui.operators.base_operator import BaseOperator
from shutterbug.gui.operators.operator_parameters import BoxSelectParameters


class BoxSelectOperator(BaseOperator):

    def __init__(
        self,
        viewer: ImageViewer,
        params: BoxSelectParameters,
        controller: AppController,
    ):
        super().__init__(viewer, controller)
        # Parameters live here
        self.params = params
        self.params.changed.connect(self._on_params_changed)

        # Initial variables
        self.start_pos = None
        self.end_pos = None
        self.rubber = None
        self.preview_items = []
        self.view = viewer.view  # type: ignore
        self.scene_rect = None

        # Debounce timer
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self._update_preview)

    def create_settings_widget(self) -> BoxSelectOperatorSettingsWidget:
        return BoxSelectOperatorSettingsWidget(self.params)

    def start(self, event: QMouseEvent):
        """Begins selection box at point of click"""
        self.start_pos = event.pos()
        self.rubber = QRubberBand(QRubberBand.Shape.Rectangle, self.view)
        self.rubber.setGeometry(QRect(event.pos(), QSize()))
        self.rubber.show()

    def stop_interaction(self):
        self._update_preview()
        self.listening = False

    def update(self, event: QMouseEvent):
        """Updates selection box on mouse move"""
        if not self.active and not self.listening:
            return
        if self.active and not self.listening:
            # Pan and drag just happened
            if self.scene_rect:
                new_rect = self.view.mapFromScene(self.scene_rect).boundingRect()

                if self.rubber:
                    self.rubber.setGeometry(new_rect)
        else:
            # Normal operation
            self.end_pos = event.pos()
            if self.start_pos and self.end_pos:
                rect = QRect(self.start_pos, self.end_pos).normalized()
                if self.rubber:
                    self.rubber.setGeometry(rect)

                # Compute scene rect
                self.scene_rect = self.view.viewport_rect_to_scene(rect)
                self.debounce_timer.stop()
                self.debounce_timer.start(42)  # ~24 fps

    def build_command(self):
        """Builds command that adds star measurements to project"""
        if not self.rubber:
            return  # No work to do

        scene_rect = self.view.viewport_rect_to_scene(self.rubber.geometry())
        stars = self._find_stars_in(scene_rect)

        if not stars or self.view.current_image is None:
            return None  # Things have gone wrong

        return AddMeasurementsCommand(stars, self.view.current_image, self.controller)

    def cleanup_preview(self):
        """Cleans preview"""
        if self.rubber:
            self.rubber.deleteLater()
            self.rubber.hide()
            self.rubber = None
        # Clear old preview items
        for item in self.preview_items:
            self.controller.markers.remove_marker(item)
        self.preview_items.clear()

    def _update_preview(self):
        """Updates preview of command"""
        # Clear old preview
        for item in self.preview_items:
            self.controller.markers.remove_marker(item)

        self.preview_items.clear()

        # Query stars using threshold
        if not self.rubber:
            return  # Something broke
        stars = self._find_stars_in(self.scene_rect)

        if not stars or self.view.current_image is None:
            return None

        # Build the preview
        for star in stars:
            circle = self.controller.markers.create_marker_from_position(
                star["xcentroid"], star["ycentroid"], self.view.current_image
            )
            self.preview_items.append(circle)

    def _find_stars_in(self, scene_rect: QRect):
        """Finds stars in a rectangle"""
        upper_left = scene_rect.topLeft()
        bottom_right = scene_rect.bottomRight()
        image = self.view.current_image
        if image is None:
            return

        centroids = self.controller.images.find_centroids_from_points(
            image, upper_left, bottom_right, threshold=self.params.threshold
        )

        return centroids

    @Slot()
    def _on_params_changed(self):
        """Handles parameters changing in Box Selection"""
        if self.active:
            self._update_preview()
