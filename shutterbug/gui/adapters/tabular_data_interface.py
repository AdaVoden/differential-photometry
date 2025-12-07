from abc import abstractmethod, ABC

from typing import List

from PySide6.QtCore import QObject, Signal


class AdapterSignals(QObject):
    # ID, column, value
    item_updated = Signal(str, int, object)
    item_removed = Signal(str)
    item_added = Signal(list)


class TabularDataInterface(ABC):
    @abstractmethod
    def get_column_headers(self) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def get_row_data(self) -> List:
        raise NotImplementedError

    @property
    @abstractmethod
    def signals(self) -> AdapterSignals:
        raise NotImplementedError
