from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton
from PySide6.QtCore import Qt, Signal, QPoint, Slot
from PySide6.QtGui import QIntValidator, QCursor, QMouseEvent, QDoubleValidator


class ScrubbySlider(QWidget):
    """A blender-like value box with drag-changing"""

    valueChanged = Signal(float)

    def __init__(
        self,
        min_val: float,
        max_val: float,
        default: float,
        number_type: str = "int",
        decimal_places: int = 3,
    ):
        super().__init__()
        self.min_val = min_val
        self.max_val = max_val
        self.current_val = default
        self.number_type = number_type
        if number_type == "int":
            self.decimal_places = 0
            self.decimal_mulitplier = 1
        else:
            self.decimal_places = decimal_places
            self.decimal_mulitplier = 1 / 10**decimal_places

        # Set up dragging variables
        self.dragging = False
        self.drag_start_pos = QPoint()
        self.drag_start_val = 0

        # Layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # Left Arrow
        self.left_btn = QPushButton("<")
        self.left_btn.clicked.connect(self.decrement)
        layout.addWidget(self.left_btn)

        # Line edit for value display and input
        if number_type == "int":

            self.line_edit = QLineEdit(str(int(default)))
            min_val = int(min_val)
            max_val = int(max_val)
            self.line_edit.setValidator(QIntValidator(min_val, max_val))
        elif number_type == "float":
            min_val = float(min_val)
            max_val = float(max_val)

            self.line_edit = QLineEdit(f"{default:.{decimal_places}f}")
            self.line_edit.setValidator(
                QDoubleValidator(min_val, max_val, decimal_places)
            )
        self.line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.line_edit.editingFinished.connect(self.on_text_changed)

        # Mouse tracking for drag functionality
        self.line_edit.setMouseTracking(True)
        self.line_edit.mousePressEvent = self.line_edit_mouse_press
        self.line_edit.mouseMoveEvent = self.line_edit_mouse_move
        self.line_edit.mouseReleaseEvent = self.line_edit_mouse_release

        layout.addWidget(self.line_edit)

        # Right arrow button
        self.right_btn = QPushButton(">")
        self.right_btn.clicked.connect(self.increment)
        layout.addWidget(self.right_btn)

    def line_edit_mouse_press(self, event: QMouseEvent):
        """Handles mouse press on the line edit widget"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Start dragging
            self.dragging = True
            self.drag_start_pos = event.globalPosition().toPoint()
            self.drag_start_val = self.current_val
            self.line_edit.setCursor(QCursor(Qt.CursorShape.SizeHorCursor))
            event.accept()
        else:
            QLineEdit.mousePressEvent(self.line_edit, event)

    def line_edit_mouse_move(self, event: QMouseEvent):
        """Handles mouse moving in slider"""
        if self.dragging:
            delta = event.globalPosition().toPoint().x() - self.drag_start_pos.x()
            # adjust sensitivity: 1 pixel = 1 unit
            new_value = self.drag_start_val + (delta * self.decimal_mulitplier)
            self.valueChanged.emit(new_value)
            event.accept()
        else:
            QLineEdit.mouseMoveEvent(self.line_edit, event)

    def line_edit_mouse_release(self, event: QMouseEvent):
        """Handles the mouse button release"""
        if event.button() == Qt.MouseButton.LeftButton and self.dragging:
            self.dragging = False
            self.line_edit.setCursor(QCursor(Qt.CursorShape.IBeamCursor))
            event.accept()
        else:
            QLineEdit.mouseReleaseEvent(self.line_edit, event)

    @Slot()
    def on_text_changed(self):
        """Handles line edit text being modified"""
        try:
            value = float(self.line_edit.text())
            self.valueChanged.emit(value)
        except ValueError:
            self.line_edit.setText(f"{self.current_val:.{self.decimal_places}f}")

    @Slot(float)
    def setValue(self, value: float):
        """Sets value of scrubby slider"""
        if self.number_type == "int":
            value = int(value)
        value = max(self.min_val, min(self.max_val, value))
        if value != self.current_val:
            self.current_val = value
            self.line_edit.setText(f"{value:.{self.decimal_places}f}")

    def value(self):
        """Returns the current value of the slider"""
        return self.current_val

    @Slot()
    def increment(self):
        """Increments slider by 1"""
        self.valueChanged.emit(self.current_val + 1 * self.decimal_mulitplier)

    @Slot()
    def decrement(self):
        """Decrements slider by 1"""
        self.valueChanged.emit(self.current_val - 1 * self.decimal_mulitplier)
