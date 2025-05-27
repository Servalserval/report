import ccxt
import pandas as pd
from datetime import datetime

UNIX_2022_01_01 = 1640966400
def fetch_binance_data():
    # 初始化交易所（例如 Binance）
    exchange = ccxt.binance()

    # 市場與時間週期（時間粒度）
    symbol = 'BTC/USDT'
    timeframe = '5m'  # 可選：'1m', '5m', '1h', '1d' 等
    limit = 1000      # 最多一次抓多少筆（取決於交易所）

    # 抓取歷史 K 線
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
