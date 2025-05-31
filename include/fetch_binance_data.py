from utils.output_data import output_data
import ccxt
import time
import tqdm


UNIX_2022_01_01 = 1640966400 * 1000
UNIX_2025_01_01 = 1735660800 * 1000

def fetch_binance_data():
    """
    Fetch the historical ohlcv of Binance 
    """
    exchange = ccxt.binance()
    symbol = 'BTC/USDT'
    timeframe = '5m'
    timeframe_in_second = 300 * 1000
    limit = 1000 

    since = UNIX_2022_01_01
    current_time = time.time() * 1000
    total_fetch = int((current_time - since) // (timeframe_in_second * limit))
    ohlcv_data = []
    for i in tqdm.tqdm(range(total_fetch)):
        res = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit, since = since + i * timeframe_in_second * limit)
        ohlcv_data.extend(res)
        time.sleep(0.25) # To prevent binance banning ip

    output_data(data = ohlcv_data, lockfile = f"data/binance_data/{since}.json")