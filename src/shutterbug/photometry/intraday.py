#     ds.coords[method] = xr.apply_ufunc(
#     tester.test,
#     ds["average_diff_mags"],
#     input_core_dims=[[dimension]],
#     vectorize=True,
# )


# @bars.progress(
#     name="iterations",
#     desc="Variable star detection iterations",
#     unit="iteration",
#     leave=False,
#     status_str="Differential Photometry per day",
#     indentation=2,
#     countable_var="iterations",
#     arg_pos=5,
# )
# def iterate_differential_photometry(
#     ds: xr.Dataset,
#     method: str = "chisquared",
#     p_value: int = 4,
#     null="accept",
#     clip=False,
#     iterations=1,
#     pbar_method=None,
#     varying_flag="varying",
# ) -> xr.Dataset:
#     logging.info("Processing day %s", ds["time.date"].values[0])
#     pbar = bars.get("iterations")
#     for i in range(0, iterations, 1):
#         # Step 1, get average differential
#         ds = dataset_differential_photometry(ds.groupby(varying_flag))
#         # Step 2, remove varying and method columns for recalculation
#         # ignore errors if columns aren't present
#         # Step 3, find varying stars via average differential
#         ds.coords[method] = xr.apply_ufunc(
#             stats.test_stationarity,
#             ds["average_diff_mags"],
#             kwargs={"method": method, "clip": clip},
#             input_core_dims=[["time"]],
#             vectorize=True,
#         )
#         if null == "accept":
#             ds.coords[varying_flag] = ds[method] >= p_value
#         else:
#             ds.coords[varying_flag] = ds[method] <= p_value

#         logging.info(
#             "Iteration %s found %s varying stars",
#             i + 1,
#             ds["intra_varying"].sum().data,
#         )
#         pbar.update()
#     if pbar_method is not None:
#         pbar_method()
#     bars.close("iterations")

#     return ds


# @bars.progress(
#     name="intra_diff",
#     desc="Calculating and finding variable intra-day stars",
#     unit="day",
#     leave=False,
#     status_str="Differential Photometry per day",
#     indentation=1,
# )
# def intra_day_iter(
#     ds: xr.Dataset,
#     varying_flag: str,
#     app_config: Dict,
#     method: str,
#     iterations: int,
# ) -> xr.Dataset:
#     intra_pbar = bars.get(
#         name="intra_diff",
#     )
#     bars.update(
#         pbar=intra_pbar, attr="total", update_to=len(np.unique(ds["time.date"]))
#     )
#     logging.info("Detecting intra-day variable stars...")
#     # No stars varying initially, need for organizing
#     ds.coords[varying_flag] = ("star", np.full(ds["star"].size, False))
#     ds = ds.groupby("time.date", restore_coord_dims=True, squeeze=False).map(
#         iterate_differential_photometry,
#         method=method,
#         iterations=iterations,
#         pbar_method=intra_pbar.update,
#         **app_config[method],
#         varying_flag=varying_flag,
#     )
#     ds[varying_flag] = ds[varying_flag].groupby("star").any(...)
#     logging.info(
#         "Detected total of %s intra-day varying stars",
#         ds[varying_flag].sum(...).values,
#     )
#     return ds