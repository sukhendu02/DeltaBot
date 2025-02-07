import requests
import pandas as pd
import time
from config import PRODUCT_SYMBOL, BASE_URL
from utils.logging_util import log_message

# Delta Exchange API Endpoint
# BASE_URL = "https://api.india.delta.exchange/v2/history/candles"

def get_historical_data(symbol, resolution="1m", limit=100):
    """
    Fetch historical OHLC data from Delta Exchange.
    """
    
    url=f"{BASE_URL}/v2/history/candles"
    headers = {
        'Accept': 'application/json'
    }
    params = {
        "resolution": resolution,
        "symbol": symbol,
        "start": int(time.time()) - (limit * 15 * 60),  # Past `limit` candles (in seconds)
        "end": int(time.time())  
    }
    
    response = requests.get(url, params=params,headers=headers)
    
    log_message(response)
    log_message(response.status_code)
    if response.status_code == 200:
        data = response.json().get("result", [])
        
        if data:
            df = pd.DataFrame(data)
            df["time"] = pd.to_datetime(df["time"], unit="s")
            df = df[::-1]  
            return df
    return None

def strategy_logic(symbol):
    """
    Trading strategy using EMA crossover + RSI + ATR-based SL/TP.
    """
    df = get_historical_data(symbol)

    if df is None or df.empty:
        log_message("NO data available")
        return None  # No data available

    # Compute Technical Indicators
    df["EMA_50"] = df["close"].ewm(span=50, adjust=False).mean()
    df["EMA_200"] = df["close"].ewm(span=200, adjust=False).mean()
    df["RSI"] = compute_rsi(df["close"], 14)
    df["ATR"] = compute_atr(df, 14)

    # Get latest values
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    entry_price = latest["close"]
    atr = latest["ATR"]

    # Risk:Reward Setup
    sl_distance = atr * 1.5
    tp_distance = sl_distance * 2.5

    log_message(latest["EMA_200"])
    log_message(latest["EMA_50"])
    log_message(latest["RSI"])

    # Entry Conditions
    if prev["EMA_50"] < prev["EMA_200"] and latest["EMA_50"] > latest["EMA_200"] and latest["RSI"] < 60:
        stop_loss = entry_price - sl_distance
        take_profit = entry_price + tp_distance
        return "buy",stop_loss,take_profit
        # return "buy"
    
    if prev["EMA_50"] > prev["EMA_200"] and latest["EMA_50"] < latest["EMA_200"] and latest["RSI"] > 40:
        stop_loss = entry_price + sl_distance
        take_profit = entry_price - tp_distance
        # return "sell"
        return "sell", stop_loss,take_profit

    return None,None,None

def compute_rsi(series, period=14):
    """Compute Relative Strength Index (RSI)."""
    delta = series.diff()  # Get the change in price
    gain = (delta.where(delta > 0, 0))  # Gain is positive change
    loss = (-delta.where(delta < 0, 0))  # Loss is negative change
    
    # Rolling average of gains and losses
    avg_gain = gain.rolling(window=period, min_periods=1).mean()  # Use min_periods to handle incomplete windows
    avg_loss = loss.rolling(window=period, min_periods=1).mean()  # Same as above
    
    # Avoid division by zero
    rs = avg_gain / avg_loss
    rs = rs.replace([float('inf'), -float('inf')], 0)  # Replace infinite values with 0 (avoid division by zero)
    
    return 100 - (100 / (1 + rs))


def compute_atr(df, period=14):
    """
    Compute Average True Range (ATR).
    """
    df["high-low"] = df["high"] - df["low"]
    df["high-close"] = abs(df["high"] - df["close"].shift(1))
    df["low-close"] = abs(df["low"] - df["close"].shift(1))
    df["true_range"] = df[["high-low", "high-close", "low-close"]].max(axis=1)
    return df["true_range"].rolling(window=period).mean()
