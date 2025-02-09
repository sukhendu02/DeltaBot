import requests
import pandas as pd
import time
import numpy as np
from config import PRODUCT_SYMBOL, BASE_URL,CANDLE_URL
from utils.logging_util import log_message

def get_historical_data(symbol, resolution="5m", limit=50):

    """Fetch historical OHLC data from Delta Exchange."""

    url = f"{CANDLE_URL}"
    headers = {
        'Accept': 'application/json'
    }
    
    params = {
        "symbol": symbol,
        "resolution": resolution,
        "start": int(time.time()) - (limit * 5 * 60),  # Past `limit` candles (in seconds)
        "end": int(time.time())
    }

    response = requests.get(url, params=params,headers=headers)
   
    if response.status_code == 200:

        data = response.json().get("result", [])
        # log_message(data)
        if data:
            df = pd.DataFrame(data)
            # df["time"] = pd.to_datetime(df["time"], unit="s")
            # df = df[::-1]  
            df = df.sort_values(by="time", ascending=True).reset_index(drop=True)
            print("Latest DataFrame:", df.tail(5))
            return df
    return None

def compute_bollinger_bands(df, window=20, num_std=2):
    """Compute Bollinger Bands (Upper, Middle, Lower)."""
    df['MA20'] = df['close'].rolling(window=window).mean()  # 20-period moving average
    df['stddev'] = df['close'].rolling(window=window).std()  # Standard deviation over the same window
    df['upper_band'] = df['MA20'] + (num_std * df['stddev'])  # Upper band
    df['lower_band'] = df['MA20'] - (num_std * df['stddev'])  # Lower band
    df['middle_band'] = df['MA20']  # Middle band is just the moving average (MA20)
    return df

def strategy_logic(symbol):
    """Bollinger Bands strategy: Buy when price reaches lower band and next candle crosses previous high."""
    df = get_historical_data(symbol)


    
    if df is None or df.empty:
        return None, None, None  # No data available
    
    # Calculate Bollinger Bands
    df = compute_bollinger_bands(df)
    
    # Get latest and previous candles
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    entry_price = latest["close"]
    log_message(latest)
    # log_message(latest['close'])
    # log_message(latest['upper_band'])
    # log_message(latest["middle_band"])
    # log_message(latest['lower_band'])

    
    # Buy Condition: Price reaches lower band and next candle crosses the previous high
    if latest['close'] <= latest['lower_band'] and latest['close'] > prev['high']:
        # Calculate stop loss and target
        stop_loss = prev['low']  # Stop loss is the low of the previous candle
        target = latest['middle_band']  # Target is the middle of Bollinger Bands (can also use a 1:2.5 RR)
        
        # Risk-to-Reward ratio calculation
        risk = entry_price - stop_loss
        reward = target - entry_price
        reward_ratio = reward / risk if risk != 0 else 0
        
        # If Reward-to-Risk ratio is acceptable (>= 2.5), execute buy
        if reward_ratio >= 2.5:
            return "buy", stop_loss, target
        
    # Sell Condition: Price reaches upper band and next candle crosses the previous low
    elif latest['close'] >= latest['upper_band'] and latest['close'] < prev['low']:
        # Calculate stop loss and target
        stop_loss = prev['high']  # Stop loss is the high of the previous candle
        target = latest['middle_band']  # Target is the middle of Bollinger Bands (can also use a 1:2.5 RR)
        
        # Risk-to-Reward ratio calculation
        risk = stop_loss - entry_price
        reward = entry_price - target
        reward_ratio = reward / risk if risk != 0 else 0
        
        # If Reward-to-Risk ratio is acceptable (>= 2.5), execute sell
        if reward_ratio >= 2.5:
            return "sell", stop_loss, target
    
    return None, None, None  # No signal
