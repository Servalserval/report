import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq

def bs_price(option_type, S, K, T, r, sigma, q=0.0):
    """Black-Scholes option price."""
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if option_type.lower() == 'call':
        return S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    elif option_type.lower() == 'put':
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)
    else:
        raise ValueError("option_type 必須是 'call' 或 'put'")

def implied_vol(option_type, S, K, T, r, market_price, q=0.0):
    """Solve for implied volatility using Brent's method."""
    def objective(sigma):
        return bs_price(option_type, S, K, T, r, sigma, q) - market_price
    
    try:
        iv = brentq(objective, 1e-6, 5.0, maxiter=500, xtol=1e-6)
        return iv
    except Exception as e:
        return None  # 找不到合理解時回傳 None
