import pandas as pd
import numpy as np
from pathlib import Path

def load_observation_data(file_path: Path) -> pd.DataFrame:
    """Load a CSV file into a pandas DataFrame."""
    # Only data cols that we care about
    usecols = ["Name", "Mag", "JD", "Error"]
    dtype_dict = {
        "Mag": np.float32,
        "JD": np.float64,
        "Error": np.float32,
    }
    df = pd.read_csv(file_path, index_col="Name", usecols=usecols, dtype=dtype_dict) # type: ignore
    df = clean_data(df)
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the DataFrame by handling missing values and duplicates."""
    df = df.dropna(axis=0, subset=["Name", "Mag", "JD"])
    df = df.drop_duplicates(subset=['Name', 'JD'])
    df = df.sort_values(by=["Name", "JD"])
    return df

def load_spatial_metadata(file_path: Path) -> pd.DataFrame:
    """Load spatial metadata from a CSV file."""
    usecols = ["Name", "X", "Y"]

    df = pd.read_csv(file_path, index_col="Name", usecols=usecols)
    df = df.dropna(subset=["Name", "X", "Y"])
    df = df.drop_duplicates(subset=['Name'])
    return df