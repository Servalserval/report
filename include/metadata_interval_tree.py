from utils import *
import os
from intervaltree import Interval, IntervalTree
from include.fetch_deribit_data import *
import tqdm

REFERENCE_PRICE_INTERVAL = 300 * 1000
LARGE_INT = 2 ** 64

class MetadataIntervalTree():
    """
    Using interval tree, finding out which option is active in every specific time
    """
    def __init__(self):
        self.interval_tree = IntervalTree()
        self.option_dict = {}
        self.reference_price = {}

        self.option_price_dict = {}
        self.option_referencing_dict = {}
    
    def add_from_file(self, file_name):
        """
        Load market list data into class
        """
        file_path = f"data/deribit_market_list/{file_name}.json"
        res = load_data(lockfile = file_path)
        for instrument_name, instrument_info in res.items():
            self.interval_tree[instrument_info["startDate"] : instrument_info["endDate"] + 1] = instrument_name
            self.option_dict[instrument_name] = instrument_info
    
    def load_reference_price(self):
        """
        Load binance reference price data into class
        """
        file_path = f"data/binance_data/1640966400000.json"
        res = load_data(lockfile = file_path)
        self.reference_price = {}
        for i in res:
            self.reference_price[i[0]] = i[1]
    
    def query_specific_time(self, timestamp):
        """
        Find out what options are active in a specific timestamp
        O(logn + k)
        """
        active = self.interval_tree[timestamp]
        instrument_name_list = [i.data for i in active]
        print(instrument_name_list)
        return instrument_name_list
    
    async def async_fetch_unfetched_data_in_time_range(self, start_time, end_time, max_expiration, min_expiration, to_reference_diff, line_name):
        """
        In a time range, find out which data should be fetched beforehand.
        Check current filepath. If data doesn't exist, then fetch.
        """
        fixed_start_time = int(int(start_time / REFERENCE_PRICE_INTERVAL) * REFERENCE_PRICE_INTERVAL + REFERENCE_PRICE_INTERVAL)
        fixed_end_time = int(int(end_time / REFERENCE_PRICE_INTERVAL) * REFERENCE_PRICE_INTERVAL)
        current_instrument_list = []
        current_instrument_dict = {}
        total_needed_instrument_list = []
        for i in tqdm.tqdm(range(int((fixed_end_time - fixed_start_time) / REFERENCE_PRICE_INTERVAL / 1000))):
            current_time = int(fixed_start_time + i * REFERENCE_PRICE_INTERVAL)
            # If too slow, try to fix this part
            current_instrument_list = self.query_specific_time(timestamp = current_time)
            current_reference_price = self.reference_price[current_time]
            closest_price = LARGE_INT
            closest_price_instrument = ""
            strike_price_list = []
            for j in current_instrument_list:
                price = j.split("-")[2]

                if price not in strike_price_list:
                    strike_price_list.append(price)

                side = j.split("-")[3]
                if side == "C":
                    # Check expiration time if it is in range
                    expiration_time = self.option_dict[j]["endDate"]
                    if expiration_time - current_time > max_expiration or expiration_time - current_time < min_expiration:
                        continue

                    if (price - current_reference_price) ** 2 < closest_price:
                        closest_price = price
                        closest_price_instrument = j

# TODO : implement the part that we need something other than ATM options
            if to_reference_diff != 0:
                pass
            
            total_needed_instrument_list.append(closest_price_instrument)
            self.option_referencing_dict[current_time] = closest_price_instrument
        
        tasks = []
        fetch_instrument_list = []
        for instrument_name in total_needed_instrument_list:
            file_dir_name = instrument_name.split("-")[1]
            file_existance = check_os_list(filedir = f"data/deribit_data/{file_dir_name}", filename = f"{instrument_name}.json")
            if not file_existance:
                tasks.append(fetch_deribit_history_options_ohlcv(instrument_info = self.option_dict[instrument_name], fetch_data_length = 86400 * 3 * 1000))
        
        res = await asyncio.gather(*tasks)
        print("Fetch instrument : ", fetch_instrument_list)



                


            


    