from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

if TYPE_CHECKING:
    from shutterbug.core.app_controller import AppController


from PySide6.QtCore import Signal

from shutterbug.core.managers.base_manager import BaseManager


class ProgressTask:

    def __init__(self, text: str, current: int, max: int, manager: ProgressManager):
        self._text = text
        self._current = current
        self._max = max
        self.manager = manager
        self.uid = uuid4().hex

    def __enter__(self):
        self.manager.started.emit(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.manager._finish_task()
        return False

    def advance(self, n: int = 1):
        """Advances current progress bar by n"""
        if self._current + n < self._max:
            self._current += n
            self.manager.changed.emit(self)

    @property
    def max(self) -> int:
        """Returns current maximum of task or 0"""
        return self._max

    @max.setter
    def max(self, max: int):
        """Sets maximum number of items"""
        if max > 0:
            self._max = max
            self.manager.changed.emit(self)

    @property
    def current(self) -> int:
        """Returns current value of progress bar"""
        return self._current

    @current.setter
    def set_value(self, value: int):
        """Sets number of completed items"""
        if value > self._max:
            self._max = value
            self._current = value
            self.manager.changed.emit(self)
        elif value > 0:
            self._current = value
            self.manager.changed.emit(self)

    @property
    def text(self) -> str:
        """Returns current task text"""
        return self._text

    @text.setter
    def text(self, text: str):
        """Sets current task's text"""
        self._text = text
        self.manager.changed.emit(self)

    @property
    def percent(self) -> int:
        """Returns current percent completion of task"""
        if self._current > 0 and self._max > 0:
            return round((self._current / self._max) * 100)
        else:
            return 0


class ProgressManager(BaseManager):

    started = Signal(ProgressTask)
    finished = Signal()
    changed = Signal(ProgressTask)

    def __init__(self, controller: AppController, parent=None):
        super().__init__(controller, parent)
        self._tasks = []  # task
        self._current_task: ProgressTask | None = None

    def __call__(self, text: str, max: int = 1) -> ProgressTask:
        new_task = ProgressTask(text, 0, max, self)
        self._tasks.append(new_task)
        self._current_task = new_task
        return new_task

    def _finish_task(self):
        self._tasks.pop()  # remove from queue
        if len(self._tasks) > 0:
            self._current_task = self._tasks[-1]
            self.changed.emit(self._current_task)
        else:
            self._current_task = None
            self.finished.emit()

    def subtask(self, text: str, max: int):
        """Creates a subtask to run and update"""
        pass
