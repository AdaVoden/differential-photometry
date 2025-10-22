import logging

import click
import pandas as pd

from shutterbug.csv_loader import load_observation_data, load_spatial_metadata
from shutterbug.differential import calculate_differential_magnitudes, find_reference_stars

@click.command()
@click.option('--data-file', type=click.Path(exists=True), required=True,
              help='Path to the CSV file containing observation data.')
def cli(data_file):
    """Command-line interface for calculating differential magnitudes."""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info(f"Loading observation data from {data_file}")
    data = load_observation_data(data_file)
    metadata = load_spatial_metadata(data_file)
    logger.info("Data loaded successfully.")
    diff_data = pd.DataFrame()

    for star in metadata['Name'].unique():
        target_star = star
        logger.info(f"Finding reference stars for target star {target_star}")
        reference_stars = find_reference_stars(metadata, target_star)

        # Calculate differential magnitudes
        logger.info(f"Calculating differential magnitudes for target star {target_star}")
        diff_mags = calculate_differential_magnitudes(data, target_star, reference_stars)

        diff_data = pd.concat([diff_data, diff_mags], ignore_index=True)

    logger.info("Differential magnitudes calculated successfully.")
    print(diff_data)