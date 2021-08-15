import xarray as xr
from shutterbug.photometry.photometry import DifferentialBase

# def inter_day(ds: xr.Dataset, app_config: Dict, method: str) -> xr.Dataset:
#     clip = app_config[method]["clip"]
#     status = bars.status
#     status.update(stage="Differential Photometry per star")

#     # TODO Throw in callback function for inter_pbars
#     inter_pbar = bars.start(
#         name="inter_diff",
#         total=len(ds.indexes["star"]),
#         desc="  Calculating and finding variable inter-day stars",
#         unit="Days",
#         color="blue",
#         leave=False,
#     )
#     # Detecting if stars are varying across entire dataset
#     logging.info("Detecting inter-day variable stars...")

#     ds.coords[method] = xr.apply_ufunc(
#         stats.test_stationarity,
#         (ds["average_diff_mags"] - ds["dmag_offset"]),
#         kwargs={"method": method, "clip": clip},
#         input_core_dims=[["time"]],
#         vectorize=True,
#     )
#     inter_pbar.update(len(ds.indexes["star"]))
#     p_value = app_config[method]["p_value"]
#     null = app_config[method]["null"]

#     logging.info(
#         "Detected %s inter-day variable stars",
#         ds["inter_varying"].groupby("star").all(...).sum(...).data,
#     )
#     return ds