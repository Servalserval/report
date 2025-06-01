from include import *
from utils import *

# Config
START_TIME = 1704038400 * 1000
END_TIME = 1706716800 * 1000
FILE_NAME = "BTC"

"""
max expiration : time until expiration. Choose the one which is closest but larger than target in milliseconds
to reference diff : for example, 0 denotes the one closest to ATM, +1 denotes the one higher than ATM, -1 denotes the one lower than ATM
"""
LINE_1 = {
    "max_expiration_range" : 86400 * 1000 * 2,
    "min_expiration_range" : 0,
    "to_reference_diff" : 0
}

class IVCalculator():
    def __init__(self):
        self.tree = MetadataIntervalTree()
        self.set_tree()
    
    def set_tree(self):
        self.tree.load_reference_price()
        self.tree.add_from_file(file_name = FILE_NAME)
    
    def fetch_unfetched_data(self):
        asyncio.get_event_loop().run_until_complete(self.tree.async_fetch_unfetched_data_in_time_range(start_time = START_TIME, end_time = END_TIME, max_expiration = LINE_1["max_expiration_range"], min_expiration = LINE_1["min_expiration_range"], to_reference_diff = LINE_1["to_reference_diff"], line_name = "line_1"))