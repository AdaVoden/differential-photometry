import logging

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

from astropy.time import Time


def plot_light_curve(df: pd.DataFrame, star_name: str, output_path: str):
    """Plot differential magnitude vs time."""
    # Convert JD to a more readable format
    logging.debug(f"Converting JD to readable time format for star {star_name}")
    times = Time(df["JD"], format="jd").to_datetime().tolist()
    # Scatter plot with error bars if you have them
    if "differential_error" in df.columns:
        plt.errorbar(
            times,
            df["differential_magnitude"],
            yerr=df["differential_error"],
            fmt="o",
            markersize=3,
            alpha=0.6,
        )
    else:
        plt.scatter(times, df["differential_magnitude"], s=10, alpha=0.6)

    # Plot formatting
    plt.tick_params(axis="x", labelrotation=45)
    plt.xlabel("Time")
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    plt.ylabel("Differential Magnitude")
    plt.title(f"Light Curve: {star_name}")
    plt.gca().invert_yaxis()  # Magnitudes decrease upward
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    # Save and close the plot
    plt.savefig(output_path, dpi=150)
    plt.close()
    logging.info(f"Light curve for {star_name} saved to {output_path}")
