from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton
from PySide6.QtCore import Qt, Signal, QPoint, Slot
from PySide6.QtGui import QIntValidator, QCursor, QMouseEvent


class ScrubbySlider(QWidget):
    """A blender-like value box with drag-changing"""

    valueChanged = Signal(int)

    def __init__(self, min_val: int, max_val: int, default: int):
        super().__init__()
        self.min_val = min_val
        self.max_val = max_val
        self.current_val = default

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
        self.line_edit = QLineEdit(str(default))
        self.line_edit.setValidator(QIntValidator(min_val, max_val))
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
            new_value = self.drag_start_val + delta
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
            value = int(self.line_edit.text())
            self.valueChanged.emit(value)
        except ValueError:
            self.line_edit.setText(str(self.current_val))

    @Slot(int)
    def setValue(self, value: int):
        """Sets value of scrubby slider"""
        value = max(self.min_val, min(self.max_val, value))
        if value != self.current_val:
            self.current_val = value
            self.line_edit.setText(str(value))

    def value(self):
        """Returns the current value of the slider"""
        return self.current_val

    @Slot()
    def increment(self):
        """Increments slider by 1"""
        self.valueChanged.emit(self.current_val + 1)

    @Slot()
    def decrement(self):
        """Decrements slider by 1"""
        self.valueChanged.emit(self.current_val - 1)
