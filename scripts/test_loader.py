from src.data.binance import load_binance_data

btc = load_binance_data(
    symbol="BTCUSDT",
    interval="4h",
    start_year=2019,
)

print(btc.head())