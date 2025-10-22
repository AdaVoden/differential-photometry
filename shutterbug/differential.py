from typing import List

import numpy as np
import pandas as pd
import logging

def calculate_differential_magnitudes(data: pd.DataFrame, 
                                      target_star: str, 
                                      reference_stars: List[str]) -> pd.DataFrame:
    """Calculates differential magnitudes for a target star against reference stars.

    :param data: DataFrame containing 'Name', 'Mag', 'JD', and 'Error' columns
    :param target_star: Name of the target star
    :param reference_stars: List of names of reference stars
    :returns: DataFrame with differential magnitudes and errors for the target star

    """
    target_data = data[data['Name'] == target_star]
    reference_data = data[data['Name'].isin(reference_stars)]

    if target_data.empty:
        raise ValueError(f"Target star {target_star} not found in data.")
    if reference_data.empty:
        raise ValueError("No reference stars found in data.")

    # Merge target and reference data on JD (time)
    merged = pd.merge(target_data, reference_data, on='JD', suffixes=('_target', '_ref'))

    # Calculate differential magnitude and error
    merged['differential_magnitude'] = merged['Mag_target'] - merged['Mag_ref']
    merged['differential_error'] = np.sqrt(merged['Error_target']**2 + merged['Error_ref']**2)
    # Average over reference stars
    merged = merged.groupby(['Name_target', 'JD'], observed=True).agg({
        'differential_magnitude': 'mean',
        'differential_error': lambda x: np.sqrt(np.sum(x**2)) / len(x),

    }).reset_index()

    result = merged[['Name_target', 'JD', 'differential_magnitude', 'differential_error']]
    result = result.rename(columns={'Name_target': 'Name'})
    return result

def find_reference_stars(metadata: pd.DataFrame, 
                         target_star: str, 
                         max_distance: float | None = None, 
                         min_refs: int=10, 
                         max_refs: int=50) -> List[str]:
    """Finds reference stars within a certain distance from the target star."""
    # Get target star position
    target_pos = metadata[metadata['Name'] == target_star][['X', 'Y']].iloc[0]

    # Calculate distances to all other stars
    metadata['distance'] = np.sqrt(
        (metadata['X'] - target_pos.X) ** 2 + 
        (metadata['Y'] - target_pos.Y) ** 2
    )

    # Sort by distance, excluding the target star itself
    nearby = metadata[metadata['Name'] != target_star].sort_values(by='distance')

    # Strategy: Take closest N stars, ensuring we get enough
    # Start with max_distance if provided, otherwise take closest max_refs
    if max_distance:
        candidates = nearby[nearby['distance'] <= max_distance]
        if len(candidates) < min_refs:
            # Not enough, expand to get minimum
            candidates = nearby.head(min_refs)
    else:
        candidates = nearby.head(max_refs)
    logging.info(f"Found {len(candidates)} reference stars for target {target_star}, maximum distance: {candidates['distance'].max():.2f} pixels")
    logging.info(f"Reference stars: {candidates['Name'].tolist()}")
    return candidates['Name'].tolist()