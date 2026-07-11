from src.data.binance import load_binance_data
from src.utils.gap_checker import gap_summary

INTERV = "15m"

btc = load_binance_data(
    symbol="XRPUSDT",
    interval=INTERV,
    start_year=2019,
)

print(btc.head())

gap_summary(btc, INTERV)
