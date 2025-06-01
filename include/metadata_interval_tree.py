from utils import *
import os
from intervaltree import Interval, IntervalTree
from include.fetch_deribit_data import *
import tqdm
import time
from include.black_scholes import *

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
        self.implied_vol_dict = {}
        self.realized_vol_dict = {}
    
    def add_from_file(self, file_name):
        """
        Load market list data into class
        """
        file_path = f"data/deribit_market_list/{file_name}.json"
        res = load_data(lockfile = file_path)
        for instrument_name, instrument_info in res.items():
            if instrument_info["endDate"] + 1 - 3600 * 1000 < instrument_info["startDate"] + 3600 * 6 * 1000:
                continue
            self.interval_tree[instrument_info["startDate"] + 3600 * 6 * 1000 : instrument_info["endDate"] + 1 - 3600 * 1000] = instrument_name
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
        return instrument_name_list
    
    def fetch_unfetched_data_in_time_range(self, start_time, end_time, max_expiration, min_expiration, to_reference_diff, line_name):
        """
        In a time range, find out which data should be fetched beforehand.
        Check current filepath. If data doesn't exist, then fetch.
        """
        fixed_start_time = int(int(start_time / REFERENCE_PRICE_INTERVAL) * REFERENCE_PRICE_INTERVAL + REFERENCE_PRICE_INTERVAL)
        fixed_end_time = int(int(end_time / REFERENCE_PRICE_INTERVAL) * REFERENCE_PRICE_INTERVAL)
        current_instrument_list = []
        current_instrument_dict = {}
        total_needed_instrument_list = []
        plus_1_total_needed_instrument_list = []
        minus_1_total_needed_instrument_list = []
        for i in tqdm.tqdm(range(int((fixed_end_time - fixed_start_time) / REFERENCE_PRICE_INTERVAL))):
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

                    if (float(price) - current_reference_price) ** 2 < closest_price:
                        closest_price = float(price)
                        closest_price_instrument = j

            closest_price_instrument_list = closest_price_instrument.split("-")

            possible_plus_1 = f"{closest_price_instrument_list[0]}-{closest_price_instrument_list[1]}-{int(closest_price_instrument_list[2]) + 500}-C"
            possible_plus_2 = f"{closest_price_instrument_list[0]}-{closest_price_instrument_list[1]}-{int(closest_price_instrument_list[2]) + 1000}-C"

            if possible_plus_1 in current_instrument_list:
                if possible_plus_1 not in plus_1_total_needed_instrument_list:
                    plus_1_total_needed_instrument_list.append(possible_plus_1)
            
            if possible_plus_2 in current_instrument_list:
                if possible_plus_2 not in plus_1_total_needed_instrument_list:
                    plus_1_total_needed_instrument_list.append(possible_plus_2)
            
            possible_minus_1 = f"{closest_price_instrument_list[0]}-{closest_price_instrument_list[1]}-{int(closest_price_instrument_list[2]) - 500}-C"
            possible_minus_2 = f"{closest_price_instrument_list[0]}-{closest_price_instrument_list[1]}-{int(closest_price_instrument_list[2]) - 1000}-C"

            if possible_minus_1 in current_instrument_list:
                if possible_minus_1 not in minus_1_total_needed_instrument_list:
                    minus_1_total_needed_instrument_list.append(possible_minus_1)
            
            if possible_minus_2 in current_instrument_list:
                if possible_minus_2 not in minus_1_total_needed_instrument_list:
                    minus_1_total_needed_instrument_list.append(possible_minus_2)

            if closest_price_instrument not in total_needed_instrument_list:
                total_needed_instrument_list.append(closest_price_instrument)

            self.option_referencing_dict[current_time] = closest_price_instrument
        
        newly_fetched_num = 0
        for instrument_name in tqdm.tqdm(total_needed_instrument_list):
            file_dir_name = instrument_name.split("-")[1]
            file_existance = check_os_list(filedir = f"data/deribit_data/{file_dir_name}", filename = f"{instrument_name}.json")
            if not file_existance:
                asyncio.get_event_loop().run_until_complete(fetch_deribit_history_options_ohlcv(instrument_info = self.option_dict[instrument_name], fetch_data_length = 86400 * 3 * 1000))
                newly_fetched_num += 1
                time.sleep(0.1)
        
        print("Fetch instrument : ", total_needed_instrument_list)
        print("Newly fetched : ", newly_fetched_num)

        check_os_list(filedir="data/iv_using_option", filename=f"{fixed_start_time}_{fixed_end_time}.json")
        output_data(data = self.option_referencing_dict, lockfile = f"./data/iv_using_option/{fixed_start_time}_{fixed_end_time}.json")
        
        newly_fetched_num = 0
        for instrument_name in tqdm.tqdm(plus_1_total_needed_instrument_list):
            file_dir_name = instrument_name.split("-")[1]
            file_existance = check_os_list(filedir = f"data/deribit_data/{file_dir_name}", filename = f"{instrument_name}.json")
            if not file_existance:
                asyncio.get_event_loop().run_until_complete(fetch_deribit_history_options_ohlcv(instrument_info = self.option_dict[instrument_name], fetch_data_length = 86400 * 3 * 1000))
                newly_fetched_num += 1
                time.sleep(0.1)

        print("Fetch instrument : ", plus_1_total_needed_instrument_list)
        print("Newly fetched : ", newly_fetched_num)

        check_os_list(filedir="data/iv_plus_1_using_option", filename=f"{fixed_start_time}_{fixed_end_time}.json")
        output_data(data = self.option_referencing_dict, lockfile = f"./data/iv_plus_1_using_option/{fixed_start_time}_{fixed_end_time}.json")

        newly_fetched_num = 0
        for instrument_name in tqdm.tqdm(minus_1_total_needed_instrument_list):
            file_dir_name = instrument_name.split("-")[1]
            file_existance = check_os_list(filedir = f"data/deribit_data/{file_dir_name}", filename = f"{instrument_name}.json")
            if not file_existance:
                asyncio.get_event_loop().run_until_complete(fetch_deribit_history_options_ohlcv(instrument_info = self.option_dict[instrument_name], fetch_data_length = 86400 * 3 * 1000))
                newly_fetched_num += 1
                time.sleep(0.1)

        print("Fetch instrument : ", minus_1_total_needed_instrument_list)
        print("Newly fetched : ", newly_fetched_num)

        check_os_list(filedir="data/iv_minus_1_using_option", filename=f"{fixed_start_time}_{fixed_end_time}.json")
        output_data(data = self.option_referencing_dict, lockfile = f"./data/iv_minus_1_using_option/{fixed_start_time}_{fixed_end_time}.json")

# TODO Add put version
    
    def load_option_price_data_file(self, instrument_name):
        human_readable_time_format = instrument_name.split("-")[1]
        file_path = f"./data/deribit_data/{human_readable_time_format}/{instrument_name}.json"
        res = load_data(lockfile = file_path)
        self.option_price_dict[instrument_name] = {}
        for i in res["payload"]["data"]:
            self.option_price_dict[instrument_name][int(i["exchangeTimestamp"])] = i["open"]
    
    def calculate_iv(self, start_time, end_time):
        fixed_start_time = int(int(start_time / REFERENCE_PRICE_INTERVAL) * REFERENCE_PRICE_INTERVAL + REFERENCE_PRICE_INTERVAL)
        fixed_end_time = int(int(end_time / REFERENCE_PRICE_INTERVAL) * REFERENCE_PRICE_INTERVAL)
        iv_using_option_file = f"./data/iv_using_option/{fixed_start_time}_{fixed_end_time}.json"
        plus_1_iv_using_option_file = f"./data/iv_plus_1_using_option/{fixed_start_time}_{fixed_end_time}.json"
        minus_1_iv_using_option_file = f"./data/iv_minus_1_using_option/{fixed_start_time}_{fixed_end_time}.json"
        iv_to_use = load_data(lockfile = iv_using_option_file)
        iv_plus_1 = load_data(lockfile = plus_1_iv_using_option_file)
        iv_minus_1 = load_data(lockfile = minus_1_iv_using_option_file)
        error_count = 0

        iv_plus_1_count = 0
        iv_minus_1_count = 0

        for current_time, instrument_name in tqdm.tqdm(iv_to_use.items()):
            try:
                current_price = self.reference_price[int(current_time)]

                if instrument_name not in self.option_price_dict.keys():
                    self.load_option_price_data_file(instrument_name=instrument_name)

                if int(current_time) in self.option_price_dict[instrument_name].keys():
                    option_market_price = self.option_price_dict[instrument_name][int(current_time)] * current_price
                
                else:
                    instrument_name = iv_plus_1[current_time]
                    if instrument_name not in self.option_price_dict.keys():
                        self.load_option_price_data_file(instrument_name=instrument_name)

                    print("Instrument name : ", instrument_name, ", keys : ", self.option_price_dict[instrument_name].keys(), ", current time : ", current_time)
                    if int(current_time) in self.option_price_dict[instrument_name].keys():
                        option_market_price = self.option_price_dict[instrument_name][int(current_time)] * current_price
                        iv_plus_1_count += 1
                    
                    else:
                        instrument_name = iv_minus_1[current_time]
                        if instrument_name not in self.option_price_dict.keys():
                            self.load_option_price_data_file(instrument_name=instrument_name)

                        if int(current_time) in self.option_price_dict[instrument_name].keys():
                            option_market_price = self.option_price_dict[instrument_name][int(current_time)] * current_price
                            iv_minus_1_count += 1
                        else:
                            error_count += 1

                        continue
                
                option_type = "call" if instrument_name.split("-")[3] == "C" else "put"
                
                strike_price = int(instrument_name.split("-")[2])
                time_to_expiration = (int(self.option_dict[instrument_name]["endDate"]) - int(current_time)) / (86400 * 1000 * 365)
                no_risk_rate = 0
                dividend_rate = 0
                
                imp_vol = implied_vol(
                    option_type = option_type,
                    S = current_price,
                    K = strike_price,
                    T = time_to_expiration,
                    r = no_risk_rate,
                    market_price = option_market_price,
                    q = dividend_rate
                )
                self.implied_vol_dict[current_time] = imp_vol
                # real_vol = realized_vol()

            except Exception as e:
                print(f"Error : instrument name : {instrument_name}, current time : {current_time}, error : {e}, traceback : {traceback.format_exc()}")
                error_count += 1

        print("Error count : ", error_count)
        print("Plus 1 count : ", iv_plus_1_count)
        print("Minus 1 count : ", iv_minus_1_count)
        check_os_list(filedir="data/implied_vol_list", filename=f"{fixed_start_time}_{fixed_end_time}.json")
        output_data(data=self.implied_vol_dict, lockfile = f"data/implied_vol_list/{fixed_start_time}_{fixed_end_time}.json")
    

                
                




                


            


    