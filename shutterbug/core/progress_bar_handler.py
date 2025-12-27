from PySide6.QtWidgets import QProgressBar, QLabel
from PySide6.QtCore import QCoreApplication


class ProgressHandler:
    def __init__(self, progress_bar: QProgressBar, label: QLabel):
        self.progress_bar = progress_bar
        self.label = label
        self.processing_text = None
        self._max = 1
        self._current = 0

    def __call__(self, processing_text: str, max: int = 1):
        self.processing_text = processing_text
        self._max = max
        return self

    def __enter__(self):
        self.progress_bar.setVisible(True)
        self._update()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.progress_bar.setValue(100)
        self.progress_bar.setVisible(False)
        self.label.setText("Ready")

        QCoreApplication.processEvents()
        return False  # Errors can propagate

    def _update(self):
        """Updates progress bar based on current and maximum"""
        if self._current > 0:
            value = round(self._max / self._current) * 100  # percent
            self.progress_bar.setValue(value)
        else:
            self.progress_bar.setValue(0)
        if self.processing_text:
            self.label.setText(self.processing_text)
        # Force UI update
        QCoreApplication.processEvents()

    @property
    def max(self) -> int:
        """Returns maximum number of items"""
        return self._max

    @max.setter
    def max(self, max: int):
        """Sets maximum number of items"""
        if max > 0:
            self._max = max
        self._update()

    @property
    def value(self) -> int:
        """Returns number of completed items"""
        return self._current

    @value.setter
    def value(self, value: int):
        """Sets number of completed items"""
        if not self._max or (self._max and value > self._max):
            self._max = value
            self._current = value
        elif value > 0:
            self._current = value
        self._update()

    def advance(self):
        """Advances current progress bar by 1"""
        self._current += 1
        self._update()

    def subtask(self, processing_text: str, max: int):
        """Creates a subtask to run and update"""
        return ProgressHandler(self.progress_bar, self.label)(processing_text, max)
