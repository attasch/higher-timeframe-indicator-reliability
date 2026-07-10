from __future__ import annotations

from pathlib import Path
from datetime import datetime
import requests

BASE_URL = "https://data.binance.vision/data/spot/monthly/klines"


class BinanceArchive:

    def __init__(self, root: str = "data/raw/binance"):
        self.root = Path(root)

    def archive_path(
        self,
        symbol: str,
        interval: str,
        filename: str,
    ) -> Path:

        folder = self.root / symbol / interval
        folder.mkdir(parents=True, exist_ok=True)

        return folder / filename

    def download_month(
        self,
        symbol: str,
        interval: str,
        year: int,
        month: int,
    ) -> Path | None:

        filename = f"{symbol}-{interval}-{year:04d}-{month:02d}.zip"

        destination = self.archive_path(
            symbol,
            interval,
            filename,
        )

        if destination.exists():
            print(f"✓ Cached: {filename}")
            return destination

        url = (
            f"{BASE_URL}/"
            f"{symbol}/"
            f"{interval}/"
            f"{filename}"
        )

        print(f"↓ Downloading {filename}")

        response = requests.get(url, timeout=30)

        if response.status_code != 200:
            print("Not available.")
            return None

        destination.write_bytes(response.content)

        return destination

    def download_range(
        self,
        symbol: str,
        interval: str,
        start_year: int,
        start_month: int = 1,
    ) -> None:

        today = datetime.today()

        for year in range(start_year, today.year + 1):

            for month in range(1, 13):

                if (
                    year == start_year
                    and month < start_month
                ):
                    continue

                if (
                    year == today.year
                    and month > today.month
                ):
                    break

                self.download_month(
                    symbol,
                    interval,
                    year,
                    month,
                )

def archives_exist(symbol: str, interval: str) -> bool:
    """
    Returns True if at least one downloaded archive exists.
    """

    archive_dir = Path("data/raw/binance") / symbol / interval

    if not archive_dir.exists():
        return False

    return any(archive_dir.glob("*.zip"))