from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController


from PySide6.QtCore import Signal

from shutterbug.core.managers.base_manager import BaseManager
from shutterbug.core.models.progress_model import ProgressModel


class ProgressManager(BaseManager):

    started = Signal()
    finished = Signal()
    changed = Signal()

    def __init__(self, controller: AppController, parent=None):
        super().__init__(controller, parent)
        self._tasks = []  # task
        self._current_task = None

    def __call__(self, text: str, max: int = 1):
        new_task = ProgressModel(text, 0, max)
        self._tasks.append(new_task)
        self._current_task = new_task
        return self

    def __enter__(self):
        self.started.emit()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._tasks.pop()  # remove from queue
        if len(self._tasks) > 0:
            self._current_task = self._tasks[-1]
            self.changed.emit()
        else:
            self._current_task = None
            self.finished.emit()

        return False  # Errors can propagate

    @property
    def max(self) -> int:
        """Returns current maximum of task or 0"""
        if self._current_task:
            return self._current_task.max
        else:
            return 0

    @max.setter
    def max(self, max: int):
        """Sets maximum number of items"""
        if max > 0 and self._current_task:
            self._current_task.max = max
            self.changed.emit()

    @property
    def current(self) -> int:
        """Returns current value of progress bar"""
        if self._current_task:
            return self._current_task.current
        else:
            return 0

    @current.setter
    def set_value(self, value: int):
        """Sets number of completed items"""
        if self._current_task:
            if value > self._current_task.max:
                self._current_task.max = value
                self._current_task.current = value
                self.changed.emit()
            elif value > 0:
                self._current_task.current = value
                self.changed.emit()

    @property
    def text(self) -> str:
        """Returns current task text"""
        if self._current_task:
            return self._current_task.text
        else:
            return "Ready"

    @text.setter
    def text(self, text: str):
        """Sets current task's text"""
        if self._current_task:
            self._current_task.text = text
            self.changed.emit()

    def advance(self, n: int = 1):
        """Advances current progress bar by n"""
        if self._current_task:
            self._current_task.current += n
            self.changed.emit()

    def subtask(self, text: str, max: int):
        """Creates a subtask to run and update"""
        pass
