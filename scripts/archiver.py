from src.data.archive import BinanceArchive

archive = BinanceArchive()

archive.download_range(
    symbol="BTCUSDT",
    interval="4h",
    start_year=2019,
)