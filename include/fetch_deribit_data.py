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
        data_path = f"./data/deribit_market_list/{underlying}.json"
        output_data(lockfile = data_path, data = data)

def fetch_deribit_history_options_ohlcv(instrument_name):
    url = "https://api.amberdata.com/markets/options/ohlcv/BTC-27DEC24-100000-C?exchange=deribit"