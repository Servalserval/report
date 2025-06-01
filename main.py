from include import *
import sys
import asyncio
from module.iv_calculator import *

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage : python3 main.py [module to call] [arguments to give]")
        print("See the 'descriptions' folder for details")
    conf = sys.argv[1]

    if conf == "fetch_binance_data":
        fetch_binance_data()
    
    if conf == "fetch_deribit_history_options_list":
        fetch_deribit_history_options_list()

    if conf == "find_data_range_for":
        find_data_range_for_BTC()
    
    if conf == "fetch_deribit_history_options_ohlcv":
        asyncio.get_event_loop().run_until_complete(
            fetch_deribit_history_options_ohlcv(
                instrument_info =  {
                    "exchange": "deribit",
                    "instrument": "BTC-10FEB25-100000-C",
                    "underlying": "BTC",
                    "startDate": 1738915620979,
                    "endDate": 1739174396535,
                    "active": True
                },
                fetch_data_length = 86400
            )
        )
    
    if conf == "query_active_option_at_specific_time":
        tree = MetadataIntervalTree()
        tree.add_from_file(file_name = "BNB")
        tree.query_specific_time(1744099925800)
    
    if conf == "check_os_list":
        check_os_list(filedir = "data/deribit_data/10APR25", filename = "BNB_USDC-10APR25-550-P.json")
    
    if conf == "fetch_unfetched_data_in_time_range":
        iv_calculator = IVCalculator()
        iv_calculator.fetch_unfetched_data()