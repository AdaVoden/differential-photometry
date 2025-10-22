import pandas as pd

def split_by_session(df, gap_threshold_days=1.0):
    """Split dataframe into separate observation sessions based on time gaps."""
    df = df.sort_values('JD').reset_index(drop=True)

    # Find gaps larger than the threshold
    time_diffs = df['JD'].diff()
    session_breaks = time_diffs > gap_threshold_days

    # Assign session IDs
    df['session'] = session_breaks.cumsum()

    return df
