from typing import Any

import enlighten

from xarray.core.dataset import Dataset
from xarray.core.dataarray import DataArray
from xarray.core.groupby import GroupBy, DataArrayGroupBy, DatasetGroupBy

# Best candidate to make into a class.
manager = None
status = None

progress_bars = {}

_indentation_to_colour = {0: "white", 1: "blue", 2: "purple"}


def init():
    global manager
    global status
    manager = enlighten.get_manager()  # set up universal progress bar manager

    status = manager.status_bar(
        status_format="{fill}Stage: {stage}{fill}{elapsed}",
        color="bold_underline_bright_white_on_lightslategray",
        justify=enlighten.Justify.CENTER,
        stage="Processing data",
        autorefresh=True,
        min_delta=0.1,
    )


def start(
    name: str,
    total: int,
    desc: str,
    unit: str,
    leave: bool = True,
    color: str = "white",
):
    global progress_bars
    pbar = get(name)
    if pbar is not None:
        close(name)

    pbar = manager.counter(total=total, desc=desc, unit=unit, leave=leave, color=color)
    progress_bars[name] = pbar
    return pbar


def build(
    name: str, desc: str, unit: str, total: int, leave: bool, indentation: int = 0
):
    desc = "  " * indentation + desc
    color = _indentation_to_colour[indentation]
    pbar = start(name=name, total=total, desc=desc, leave=leave, unit=unit, color=color)
    pbar.refresh()
    return pbar


def get(name: str):
    global progress_bars
    if name in progress_bars.keys():
        return progress_bars[name]
    else:
        return None


def close_all():
    global progress_bars
    for pbar in progress_bars.values():
        pbar.close()
    progress_bars.clear()
    return True


def close(name: str):
    global progress_bars
    if name in progress_bars.keys():
        try:
            progress_bars[name].close()
        except KeyError:  # already closed
            progress_bars.pop(name, None)
        progress_bars.pop(name, None)
    return True


def update(pbar: enlighten.Counter, attr: str, update_to: Any):
    setattr(pbar, attr, update_to)
    pbar.refresh()
    return True


def xarray(**pbar_args):
    # stolen from tqdm
    def inner_generator(xr_func="map"):
        def inner(ds, func, *args, **kwargs):

            total = pbar_args.pop("total", None)

            if total is None:
                if isinstance(ds, GroupBy):
                    total = len(ds)
                elif isinstance(ds, DataArray):
                    total = ds.size
                else:
                    total = len(ds.data_vars)
            bar = build(total=total, **pbar_args)

            def wrapper(*args, **kwargs):
                bar.update()
                return func(*args, **kwargs)

            try:
                return getattr(ds, xr_func)(wrapper, **kwargs)
            finally:
                if "name" in pbar_args.keys():
                    close(pbar_args["name"])

        return inner

    # monkey patching
    DataArray.progress_map = inner_generator()
    DataArrayGroupBy.progress_map = inner_generator()

    Dataset.progress_map = inner_generator()
    DatasetGroupBy.progress_map = inner_generator()
