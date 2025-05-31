from include import *
import sys

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage : python3 main.py [module to call] [arguments to give]")
        print("See the 'descriptions' folder for details")
    conf = sys.argv[1]

    if conf == "fetch_binance_data":
        fetch_binance_data()
    
    if conf == "fetch_deribit_history_options_list":
        fetch_deribit_history_options_list()
    
