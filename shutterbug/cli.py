import logging

import click
import pandas as pd

from shutterbug.csv_loader import load_observation_data, load_spatial_metadata
from shutterbug.differential import (
    calculate_differential_magnitudes,
    find_reference_stars,
)
from shutterbug.graph import plot_light_curve
from shutterbug.utility import split_by_session


@click.command()
@click.option(
    "--data-file",
    type=click.Path(exists=True),
    required=True,
    help="Path to the CSV file containing observation data.",
)
def cli(data_file):
    """Command-line interface for calculating differential magnitudes."""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Load data and set up empty DataFrame for results
    logger.info(f"Loading observation data from {data_file}")
    data = load_observation_data(data_file)
    metadata = load_spatial_metadata(data_file)
    logger.info("Data loaded successfully.")
    diff_data = pd.DataFrame()

    # Iterate over each star in the dataset, find reference stars, and calculate differential magnitudes
    for star in metadata["Name"].unique():
        target_star = star
        logger.debug(f"Finding reference stars for target star {target_star}")
        reference_stars = find_reference_stars(metadata, target_star)

        # Calculate differential magnitudes
        logger.info(
            f"Calculating differential magnitudes for target star {target_star}"
        )
        diff_mags = calculate_differential_magnitudes(
            data, target_star, reference_stars
        )

        diff_data = pd.concat([diff_data, diff_mags], ignore_index=True)

    logger.info("Differential magnitudes calculated successfully.")

    # Split data by observation sessions
    diff_data = split_by_session(diff_data)
    # Plot light curves for each session
    for session_id in diff_data["session"].unique():

        session_data = diff_data[diff_data["session"] == session_id]
        logger.info(
            f"Processing session {session_id} with {len(session_data)} observations."
        )

        # Plot light curves for each target star
        for star in session_data["Name"].unique():

            star_data = session_data[session_data["Name"] == star]
            output_path = f"{star}_{session_id}_light_curve.png"

            logger.debug(f"Plotting light curve for star {star}")
            plot_light_curve(star_data, star, output_path)
