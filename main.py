from include.fetch_binance_data import fetch_binance_data
import sys

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage : python3 main.py [module to call] [arguments to give]")
        print("See the 'descriptions' folder for details")
    conf = sys.argv[1]

    if conf == "binance_data":
        fetch_binance_data()