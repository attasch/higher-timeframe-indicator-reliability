from __future__ import annotations

import pandas as pd

from src.indicators.rsi import calculate_rsi


def calculate_stoch_rsi(
    df: pd.DataFrame,
    rsi_period: int = 14,
    stoch_period: int = 14,
    smooth_k: int = 3,
    smooth_d: int = 3,
) -> pd.DataFrame:
    """
    Calculate Stochastic RSI.

    Adds:
        rsi
        stoch_rsi
        k
        d
    """

    df = calculate_rsi(
        df.copy(),
        period=rsi_period,
    )

    lowest_rsi = (
        df["rsi"]
        .rolling(stoch_period)
        .min()
    )

    highest_rsi = (
        df["rsi"]
        .rolling(stoch_period)
        .max()
    )

    df["stoch_rsi"] = (
        (df["rsi"] - lowest_rsi)
        /
        (highest_rsi - lowest_rsi)
    )

    df["stoch_k"] = (
        df["stoch_rsi"]
        .rolling(smooth_k)
        .mean()
        * 100
    )

    df["stoch_d"] = (
        df["stoch_k"]
        .rolling(smooth_d)
        .mean()
    )

    return df