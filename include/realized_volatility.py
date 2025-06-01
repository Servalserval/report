import numpy
import math

INTERVAL = 60 * 5 * 1000

def realized_volatility(price_dict, start_time, end_time):
    log_return_list = []
    for current_time in numpy.arange(start_time, end_time, INTERVAL):
        log_price_diff = math.log(price_dict[current_time] / price_dict[current_time - INTERVAL])
        log_return_list.append(log_price_diff)
    
    mean = numpy.mean(log_return_list)
    std = numpy.std(log_return_list, ddof=1)  # 使用樣本標準差
    return std
