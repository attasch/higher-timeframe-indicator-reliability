from __future__ import annotations

from datetime import datetime
from io import BytesIO
import zipfile

import pandas as pd
import requests


BASE_URL = "https://data.binance.vision/data/spot/monthly/klines"


def _generate_file_names(
    symbol: str,
    interval: str,
    start_year: int,
    start_month: int,
    end_year: int,
    end_month: int,
) -> list[str]:
    """
    Generate monthly Binance archive filenames.
    """

    files = []

    for year in range(start_year, end_year + 1):
        for month in range(1, 13):

            if year == start_year and month < start_month:
                continue

            if year == end_year and month > end_month:
                continue

            files.append(
                f"{symbol}-{interval}-{year:04d}-{month:02d}.zip"
            )

    return files


def _download_month(
    symbol: str,
    interval: str,
    file_name: str,
) -> pd.DataFrame | None:
    """
    Download one month of Binance data.
    """

    url = f"{BASE_URL}/{symbol}/{interval}/{file_name}"

    response = requests.get(url, timeout=20)

    if response.status_code != 200:
        print(f"Skipping {file_name}")
        return None

    with zipfile.ZipFile(BytesIO(response.content)) as z:

        csv_name = z.namelist()[0]

        with z.open(csv_name) as f:

            df = pd.read_csv(f, header=None)

    return df

def _convert_timestamp(series: pd.Series) -> pd.Series:
    """
    Convert Binance timestamps.
    Handles:
    - milliseconds
    - microseconds
    - nanoseconds
    """

    series = pd.to_numeric(series)

    result = pd.Series(
        index=series.index,
        dtype="datetime64[ns]"
    )

    # milliseconds (~1.7 trillion)
    ms = series < 10**13

    # microseconds (~1.7 quadrillion)
    us = (series >= 10**13) & (series < 10**16)

    # nanoseconds (~1.7 quintillion)
    ns = series >= 10**16

    result.loc[ms] = pd.to_datetime(
        series.loc[ms],
        unit="ms",
    )

    result.loc[us] = pd.to_datetime(
        series.loc[us],
        unit="us",
    )

    result.loc[ns] = pd.to_datetime(
        series.loc[ns],
        unit="ns",
    )

    return result

def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rename columns and convert timestamps.
    """

    df.columns = [
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_volume",
        "trades",
        "taker_base_volume",
        "taker_quote_volume",
        "ignore",
    ]

    df["open_time"] = _convert_timestamp(
        df["open_time"]
    )

    df["close_time"] = _convert_timestamp(
        df["close_time"]
    )

    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "quote_volume",
        "taker_base_volume",
        "taker_quote_volume",
    ]

    df[numeric_columns] = df[numeric_columns].astype(float)

    df["trades"] = df["trades"].astype(int)

    return df


from pathlib import Path
from src.data.archive import BinanceArchive, archives_exist


def load_binance_data(
    symbol: str,
    interval: str,
    start_year: int,
    start_month: int = 1,
    refresh: bool = False,
) -> pd.DataFrame:

    processed = processed_file(symbol, interval)

    # ---------------------------------------------------
    # Fastest path
    # ---------------------------------------------------

    if processed.exists() and not refresh:

        print("Loading processed dataset...")

        return load_processed(symbol, interval)

    archive = BinanceArchive()

    # ---------------------------------------------------
    # Download only if necessary
    # ---------------------------------------------------

    if not archives_exist(symbol, interval):

        print("No archive found. Downloading historical data...")

        archive.download_range(
            symbol=symbol,
            interval=interval,
            start_year=start_year,
            start_month=start_month,
        )

    else:

        print("Using cached archives.")

    # ---------------------------------------------------
    # Build processed dataframe
    # ---------------------------------------------------

    print("Building dataframe...")

    df = build_dataframe_from_archives(
        symbol,
        interval,
    )

    save_processed(
        df,
        symbol,
        interval,
    )

    print("Processed dataset saved.")

    return df


def processed_file(symbol: str, interval: str) -> Path:
    """
    Location of the processed CSV.
    """

    folder = Path("data/processed/binance") / symbol
    folder.mkdir(parents=True, exist_ok=True)

    return folder / f"{interval}.csv"

def build_dataframe_from_archives(
    symbol: str,
    interval: str,
) -> pd.DataFrame:
    """
    Read every cached archive and merge into one dataframe.
    """

    archive_dir = Path("data/raw/binance") / symbol / interval

    zip_files = sorted(archive_dir.glob("*.zip"))

    if not zip_files:
        raise ValueError("No archived data found.")

    dfs = []

    for zip_path in zip_files:

        with zipfile.ZipFile(zip_path) as z:

            csv_name = z.namelist()[0]

            with z.open(csv_name) as f:

                dfs.append(
                    pd.read_csv(
                        BytesIO(f.read()),
                        header=None,
                    )
                )

    merged = pd.concat(
        dfs,
        ignore_index=True,
    )

    return _clean_dataframe(merged)

def load_processed(symbol: str, interval: str) -> pd.DataFrame:

    df = pd.read_csv(
        processed_file(symbol, interval),
    )

    df["open_time"] = pd.to_datetime(
        df["open_time"],
    )

    df["close_time"] = pd.to_datetime(
        df["close_time"],
    )

    return df

def save_processed(
    df: pd.DataFrame,
    symbol: str,
    interval: str,
) -> None:

    df.to_csv(
        processed_file(symbol, interval),
        index=False,
    )

