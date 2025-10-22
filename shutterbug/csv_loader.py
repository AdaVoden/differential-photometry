import logging
import pandas as pd
import numpy as np
from pathlib import Path


def load_observation_data(file_path: Path) -> pd.DataFrame:
    """Load a CSV file into a pandas DataFrame."""
    # Only data cols that we care about
    usecols = ["Name", "Mag", "JD", "Error"]
    dtype_dict = {
        "Name": "category",
        "Mag": np.float32,
        "JD": np.float64,
        "Error": np.float32,
    }

    logging.info(f"Loading observation data from {file_path}")
    df = pd.read_csv(file_path, usecols=usecols, dtype=dtype_dict)  # type: ignore
    df = clean_data(df)
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the DataFrame by handling missing values and duplicates."""
    logging.info("Cleaning observation data")
    df = df.dropna(axis=0, subset=["Mag", "JD"])
    df = df.drop_duplicates(subset=["Name", "JD"])
    df = df.sort_values(by=["Name"])
    return df


def load_spatial_metadata(file_path: Path) -> pd.DataFrame:
    """Load spatial metadata from a CSV file."""

    usecols = ["Name", "X", "Y"]

    logging.info(f"Loading spatial metadata from {file_path}")
    df = pd.read_csv(file_path, usecols=usecols)
    logging.debug(f"Spatial metadata columns: {df.columns.tolist()}")
    logging.debug("Cleaning spatial metadata")
    df = df.drop_duplicates(subset=["Name"])
    df = df.dropna(subset=["Name", "X", "Y"])
    return df
