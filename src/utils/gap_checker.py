from __future__ import annotations

import pandas as pd


INTERVALS = {
    "1m": "1min",
    "3m": "3min",
    "5m": "5min",
    "15m": "15min",
    "30m": "30min",
    "1h": "1h",
    "2h": "2h",
    "4h": "4h",
    "6h": "6h",
    "8h": "8h",
    "12h": "12h",
    "1d": "1D",
    "3d": "3D",
    "1w": "1W",
}


def check_gaps(df: pd.DataFrame, interval: str) -> pd.DataFrame:
    """
    Check for missing candles in a dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing an 'open_time' column.

    interval : str
        Binance interval (e.g. '15m', '1h', '1d').

    Returns
    -------
    pd.DataFrame
        DataFrame describing every detected gap.
    """

    if interval not in INTERVALS:
        raise ValueError(f"Unsupported interval: {interval}")

    df = df.sort_values("open_time").reset_index(drop=True)

    expected_delta = pd.Timedelta(INTERVALS[interval])

    diffs = df["open_time"].diff()

    gap_rows = df.loc[diffs > expected_delta].copy()

    if gap_rows.empty:
        print("✅ No gaps found.")
        return pd.DataFrame()

    previous_time = df["open_time"].shift()

    gap_rows["gap_start"] = previous_time.loc[gap_rows.index]
    gap_rows["gap_end"] = gap_rows["open_time"]

    gap_rows["gap_duration"] = (
        gap_rows["gap_end"] - gap_rows["gap_start"]
    )

    gap_rows["missing_candles"] = (
        gap_rows["gap_duration"] / expected_delta
    ).astype(int) - 1

    return gap_rows[
        [
            "gap_start",
            "gap_end",
            "gap_duration",
            "missing_candles",
        ]
    ]


def gap_summary(df: pd.DataFrame, interval: str) -> None:
    """
    Print a summary of missing candles.
    """

    gaps = check_gaps(df, interval)

    total_rows = len(df)

    if gaps.empty:
        print(f"Rows: {total_rows:,}")
        print("Missing candles: 0")
        print("Gap percentage: 0.0000%")
        return

    missing = gaps["missing_candles"].sum()

    pct = 100 * missing / (total_rows + missing)

    print("=" * 50)
    print("DATA QUALITY REPORT")
    print("=" * 50)
    print(f"Rows in dataset      : {total_rows:,}")
    print(f"Number of gaps       : {len(gaps)}")
    print(f"Missing candles      : {missing:,}")
    print(f"Gap percentage       : {pct:.5f}%")
    print("=" * 50)
    