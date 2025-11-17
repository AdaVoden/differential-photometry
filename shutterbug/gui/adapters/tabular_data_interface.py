from abc import abstractmethod, ABC

from typing import List


class TabularDataInterface(ABC):
    @abstractmethod
    def get_column_headers(self) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def get_row_data(self):
        raise NotImplementedError
