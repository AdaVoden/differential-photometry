from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import gc
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import shutterbug.output.figure as plot_util
import shutterbug.output.folder as io
import shutterbug.ux.progress_bars as bars
import xarray as xr

manager = None
status = None


def plot_and_save_all(
    ds: xr.Dataset,
    plot_config: Dict,
    uniform_y_axis: bool,
    offset: bool,
    dataset: Path,
    output_config: Dict,
    filename: str,
):
    logging.info("Starting graphing...")
    ds = ds.swap_dims({"star": "intra_varying"})
    ds = ds.set_index(varying=("intra_varying", "inter_varying"))
    bars.xarray(
        name="folders",
        desc="Plotting into folders",
        unit="folder",
        leave=False,
        indentation=1,
    )
    bars.status.update(stage="Graphing")
    ds.groupby("varying").progress_map(
        multiprocess_save,
        offset=offset,
        uniform=uniform_y_axis,
        plot_config=plot_config,
        dataset=dataset,
        output_config=output_config,
        filename=filename,
    )

    logging.info("Finished graphing")
    return ds.reset_index("varying")


def generate_data_folders(
    ds: xr.Dataset,
    uniform_y_axis: bool,
    offset: bool,
    filename: str,
    output_config: Dict,
) -> xr.Dataset:
    intra, inter = np.unique(ds["varying"])[0]
    ds.attrs["output_folder"] = io.generate_graph_output_path(
        offset=offset,
        uniform=uniform_y_axis,
        intra_varying=intra,
        inter_varying=inter,
        output_config=output_config,
        filename=filename,
    )
    return ds


def setup_plot_dataset(
    ds: xr.Dataset,
    offset: bool,
    uniform: bool,
    filename: str,
    output_config: Dict,
) -> xr.Dataset:
    ds = ds.pipe(
        generate_data_folders,
        uniform_y_axis=uniform,
        offset=offset,
        filename=filename,
        output_config=output_config,
    )
    ds = ds.reset_index("varying").swap_dims({"varying": "star"})
    if offset == True:
        ds["mag"] = ds["mag"].groupby("time.date") - ds["mag_offset"]
        ds["average_diff_mags"] = (
            ds["average_diff_mags"].groupby("time.date") - ds["dmag_offset"]
        )
    if uniform == True:
        pass  # do something here

    # ds = ds.stack(time_stack={"time", "time.date"})
    return ds


def multiprocess_save(
    ds: xr.Dataset,
    plot_config: Dict,
    uniform: bool,
    offset: bool,
    dataset: Path,
    output_config: Dict,
    filename: str,
):
    """Runner function, sets up multiprocess graphing for system

    Parameters
    ----------
    star_frames : pd.DataFrame
        Dataframes that contain all necessary star data
    mag_max_variation : float, optional
        The maximum magnitude variation of the dataset, for y-lim, by default None
    diff_max_variation : float, optional
        The maximum differential magnitude variation of the dataset, for y-lim, by default None
    save : bool, optional
        Switch to save or graph and display, by default False
    """
    global frame  # Shares for threads
    # Mulitprocess to speed up awful plotting code
    # pbar_folders = bars.get_progress_bar(
    #     name="folders",
    #     total=len(star_frames),
    #     desc="Plotting folders",
    #     unit="folders",
    #     color="blue",
    #     leave=False,
    # )
    frame = setup_plot_dataset(
        ds=ds,
        offset=offset,
        uniform=uniform,
        filename=filename,
        output_config=output_config,
    )

    pbar = bars.build(
        name="plot_and_save",
        total=frame["star"].size,
        desc="Making and saving graphs",
        unit="graph",
        indentation=2,
        leave=False,
    )
    logging.info("Writing to folder %s", ds.attrs["output_folder"])
    # for _, stars in frame.groupby("star"):
    #     build_and_save_figure(
    #         ds=stars,
    #         plot_config=plot_config,
    #     )
    #     pbar.update()

    with ProcessPoolExecutor(max_workers=(cpu_count() - 1)) as executor:
        futures = {
            executor.submit(
                build_and_save_figure,
                ds=stars,
                plot_config=plot_config,
            )
            for _, stars in frame.groupby("star")
        }
        for future in as_completed(futures):
            pbar.update()
            future.result()
    bars.close("plot_and_save")
    gc.collect()

    return frame


def build_and_save_figure(
    ds: xr.Dataset,
    plot_config: Dict,
) -> xr.Dataset:
    if all(lim in ds.attrs.keys() for lim in ["mag_var", "diff_var"]):
        mag_lim = limits_from_median(ds["mag"], ds.attrs["mag_var"])
        diff_lim = limits_from_median(ds["average_diff_mags"], ds.attrs["diff_var"])
    else:
        mag_lim = None
        diff_lim = None

    # Needs to be set here so each worker
    # Has the same settings
    figure = plot_util.WorkerFigure(
        nrows=2,
        ncols=len(np.unique(ds["time.date"])),
        figsize=(5 * len(np.unique(ds["time.date"])), 10),
        output_folder=ds.attrs["output_folder"],
        plot_config=plot_config,
    )

    ds.groupby("time.date").map(
        create_2x1_raw_diff_plot,
        figure=figure,
        plot_config=plot_config,
        mag_lim=mag_lim,
        diff_lim=diff_lim,
    )

    figure.share_columns_x()
    figure.share_rows_y()
    figure.set_label_outer()
    figure.set_date_formatter()
    figure.set_super_title(
        name=str(ds["star"].data),
        x=ds["x"].data,
        y=ds["y"].data,
        comparison_stars=ds["reference_stars"].data[0],
        test_statistic=ds["adfuller"].data,
    )
    figure.save(str(ds["star"].data))
    return ds  # placeholder


def limits_from_median(
    ydata: List[float], max_variation: float = None
) -> Tuple[float, float]:
    if max_variation is None:
        return None
    median = np.median(ydata)
    return (median - max_variation, median + max_variation)


def create_2x1_raw_diff_plot(
    ds: xr.Dataset,
    figure: plot_util.WorkerFigure,
    plot_config: Dict,
    mag_lim: float = None,
    diff_lim: float = None,
) -> xr.Dataset:
    axes = figure.get_next_axis()

    # Raw Magnitude
    plot_line_scatter(
        x=ds["time"].data,
        y=ds["mag"].data,
        ylabel=plot_config["magnitude"]["ylabel"],
        xlabel=plot_config["magnitude"]["xlabel"],
        color=plot_config["magnitude"]["color"],
        error=ds["error"].data,
        axes=axes[0],
        yrange=mag_lim,
        plot_config=plot_config,
    )
    # Differential Magnitude
    plot_line_scatter(
        x=ds["time"].data,
        y=ds["average_diff_mags"].data,
        ylabel=plot_config["differential_magnitude"]["ylabel"],
        xlabel=plot_config["differential_magnitude"]["xlabel"],
        color=plot_config["differential_magnitude"]["color"],
        error=ds["average_uncertainties"].data,
        axes=axes[1],
        yrange=diff_lim,
        plot_config=plot_config,
    )
    figure.set_current_column_title(str(np.unique(ds["time.date"])[0]))
    return ds


def plot_line_scatter(
    x: List[float],
    y: List[float],
    ylabel: str,
    xlabel: str,
    error: List[float],
    axes: List[plt.Axes],
    plot_config: Dict,
    color: str = "blue",
    yrange: Tuple[float, float] = None,
):
    """Creates Two plots with inputted axes, one scatter and one line.
    The scatter plot is made with errorbars, the line plot is made with fill between
    error.

    Parameters
    ----------
    x : List[float] or List[Time]
        Numerical x-data.
    y : List[float]
        Numerical y-data
    ylabel : str
        Label of the y-axis
    xlabel : str
        Label of the x-axis
    error : List[float]
        Error of the y-data
    axes : axes
        Axis objects to plot in
    color : str, optional
        Colour information for plots, by default "blue"
    yrange : Tuple[float, float], optional
        The lower and upper limits of the y-axis for this set of plots, by default None
    """
    # For the fill between error bars
    error_plus = y + error
    error_neg = y - error

    fill_between = {
        "x": x,
        "y1": error_plus,
        "y2": error_neg,
        "color": color,
        **plot_config["error"]["fill"],
    }
    error_settings = {"x": x, **plot_config["error"]["bar"]}

    sns.scatterplot(ax=axes, x=x, y=y, ci=None, color=color, animated=True)
    axes.errorbar(y=y, yerr=error, label="Error", **error_settings)
    axes.set_xlabel(xlabel)
    axes.set_ylabel(ylabel)
    axes.legend()
    if yrange is not None:
        ax.set_ylim(yrange)
