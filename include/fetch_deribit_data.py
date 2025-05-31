from utils.send_request import *
from utils.output_data import output_data
from keys.amberdata import *
import json
import traceback

headers = {
    "accept": "application/json",
    "Accept-Encoding": "gzip, deflate, br",
    "x-api-key": amberdata_api_key
}

def fetch_deribit_history_options_list():
    """
    Fetch the list of expired markets in deribit
    This function is very slow. The url of the next page is returned in cursor.
    Also, there is no params to tell which time range or which underlying.
    """
    url = "https://api.amberdata.com/markets/options/tickers/information"
    params = {
        "exchange" : "deribit",
        "includeInactive" : True
    }
    status = 200
    decoded_history_option_list = {}
    num_of_decoded_options = {}
    loop_num = 0
    while status == 200:
        try:
            loop_num += 1
            res = send_request(url = url, method = "get", params = params, header = headers)
            url = res["payload"]["metadata"]["next"]
            status = res["status"]
            data = res["payload"]["data"]
            for i in data:
                underlying = i["underlying"]
                instrument_name = i["instrument"]
                if underlying not in decoded_history_option_list.keys():
                    decoded_history_option_list[underlying] = {}
                    num_of_decoded_options[underlying] = 0
                decoded_history_option_list[underlying][instrument_name] = i
                num_of_decoded_options[underlying] += 1
            print("Executing fetch deribit history option list : ", loop_num, num_of_decoded_options)
        except Exception as e:
            print("Fetch deribit history option list error : ", e, ", traceback : ", traceback.format_exc())
            break

    for underlying, data in decoded_history_option_list.items():
        try:
            data_path = f"./data/deribit_market_list/{underlying}.json"
            output_data(lockfile = data_path, data = data)
        except Exception as e:
            print(f"Can't output data for underlying : {underlying}")

async def fetch_deribit_history_options_ohlcv(instrument_info, fetch_data_length : int):
    """
    Fetch the historical ohlcv for a specific deribit history option
    Params : 
    instrument_info : The info format obtained in fetch_deribit_history_options_list.
    fetch_data_length : The amount of seconds needed for the data range.
    """
    url = f"https://api.amberdata.com/markets/options/ohlcv/{instrument_info['instrument']}"
    end_time = instrument_info["endDate"]
    fetch_data_until = end_time
    params = {
        "exchange" : "deribit",
        "includeInactive" : True
    }
