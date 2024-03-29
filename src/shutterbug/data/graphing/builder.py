from abc import abstractmethod
from datetime import date
from typing import Dict, Literal, Optional, Tuple

import pandas as pd
from attrs import define, field
from shutterbug.data.interfaces.internal import Graph


@define(slots=True)
class BuilderBase:
    """Generic builder type, contains all fields and properties for building"""

    title: Optional[str] = field(init=False, default=None)
    axis_names: Tuple[Optional[str], Optional[str]] = field(
        init=False, default=(None, None)
    )
    axis_limits: Tuple[Optional[float], Optional[float]] = field(
        init=False, default=(None, None)
    )
    data: pd.Series = field(init=False)
    error: pd.Series = field(init=False)
    size: Tuple[Optional[int], Optional[int]] = field(init=False, default=(None, None))

    type: Literal["scatter", "line"] = field(init=False, default="scatter")
    error_display: Literal["bar", "fill", None] = field(init=False, default="bar")
    features: Dict[date, Dict[str, float]] = field(init=False, default={})

    def reset(self) -> None:
        self.title = None
        self.axis_names = (None, None)
        self.axis_limits = (None, None)
        # set dtype to avoid deprecation warning
        # float16 to keep it small
        self.data = pd.Series(dtype="float16")
        self.error = pd.Series(dtype="float16")
        self.size = (None, None)
        self.features = {}
        self.type = "scatter"
        self.error_display = "bar"

    @abstractmethod
    def build(self) -> Graph:
        raise NotImplementedError
