from __future__ import annotations

import pandas as pd


def calculate_rsi(
    df: pd.DataFrame,
    period: int = 14,
) -> pd.DataFrame:
    """
    Calculate Wilder's RSI.

    Adds a new column:
        rsi
    """

    delta = df["close"].diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1 / period,
        adjust=False,
    ).mean()

    avg_loss = loss.ewm(
        alpha=1 / period,
        adjust=False,
    ).mean()

    rs = avg_gain / avg_loss

    df = df.copy()

    df["rsi"] = 100 - (100 / (1 + rs))

    return df