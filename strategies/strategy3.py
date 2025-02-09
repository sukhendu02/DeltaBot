import requests
import pandas as pd
import time
import numpy as np
from config import PRODUCT_SYMBOL, BASE_URL
from utils.logging_util import log_message
# import websocket


def get_historical_data(symbol, resolution="5m", limit=100):

    """Fetch historical OHLC data from Delta Exchange."""

    url = f"https://api.india.delta.exchange/v2/history/candles"
    headers = {
        'Accept': 'application/json'
    }
    # end_time = int(time.time())  
    end_time = int(time.time())
    
    # Go back only a reasonable window (e.g., 1-2 days, not too far)
    # start_time = end_time - (limit * 60 * 60) -3600 # 2000 candles of 5-min each
    start_time=end_time - (limit * 5 * 60)
    params = {
        "resolution": resolution,
        "symbol": symbol,
        "start":start_time ,  # Past `limit` candles (in seconds)
        "end": end_time,
    }

    # log_message(int(time.time()))

    response = requests.get(url, params=params,headers=headers)
    
    # log_message(response.status_code)
   
    if response.status_code == 200:

        # data = response.json().get("result", [])
        # log_message(data)
        # if data:
        #     df = pd.DataFrame(data)
        #     df["time"] = pd.to_datetime(df["time"], unit="s")
        #     # df = df[::-1]  

        #     # df["time"] = pd.to_datetime(df["time"], unit="s")
        #     # 🔹 Sort by time in descending order (latest first
        #     # df = df.sort_values(by="time", ascending=False).reset_index(drop=True)

        #                 # Convert UNIX timestamp to readable datetime
        #     df["time"] = pd.to_datetime(df["time"], unit="s")

        #     # 🔹 Sort by time in descending order (latest first)
        #     # df = df.sort_values(by="time", ascending=False).reset_index(drop=True)


        #     return df

        
        data = response.json().get("result", [])
        # log_message(data)
        if data:
            df = pd.DataFrame(data)
            # df["time"] = pd.to_datetime(df["time"], unit="s")
            # df["time"]=pd.Timestamp.date()
            df = df.sort_values(by="time", ascending=True).reset_index(drop=True)
            # print("Latest DataFrame:", df.tail(5))
            
            return df
    return None

def compute_ema(series, period):
    """
    Compute Exponential Moving Average (EMA).
    """
    return series.ewm(span=period, adjust=False).mean()

def compute_rsi(series, period=14):
    """
    Compute Relative Strength Index (RSI).
    """
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(window=period, min_periods=1).mean()
    avg_loss = pd.Series(loss).rolling(window=period, min_periods=1).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return pd.Series(rsi, index=series.index)

def compute_atr(df, period=14):
    """
    Compute Average True Range (ATR).
    """
    df["tr1"] = df["high"] - df["low"]
    df["tr2"] = abs(df["high"] - df["close"].shift(1))
    df["tr3"] = abs(df["low"] - df["close"].shift(1))
    df["true_range"] = df[["tr1", "tr2", "tr3"]].max(axis=1)
    df["ATR"] = df["true_range"].rolling(window=period).mean()
    return df["ATR"]

def compute_vwap(df):
    """
    Compute VWAP (Volume-Weighted Average Price).
    """
    df["cum_vol"] = df["volume"].cumsum()
    df["cum_vol_price"] = (df["close"] * df["volume"]).cumsum()
    df["VWAP"] = df["cum_vol_price"] / df["cum_vol"]
    return df["VWAP"]

def strategy_logic(symbol):
    """
    Scalping Strategy using EMA, RSI, VWAP, and ATR-based SL/TP.
    """
    df = get_historical_data(symbol)

    if df is None or df.empty:
        return None, None, None  # No data available
    
    # df_list = df.to_dict(orient="records")
    # print(df_list)
    print("Latest DataFrame:", df.tail(5))

    # Compute Technical Indicators
    df["EMA_9"] = compute_ema(df["close"], 9)
    df["EMA_21"] = compute_ema(df["close"], 21)
    df["RSI"] = compute_rsi(df["close"], 14)
    df["ATR"] = compute_atr(df, 14)
    df["VWAP"] = compute_vwap(df)

    # Get latest values
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    entry_price = latest["close"]
    atr = latest["ATR"]

    # log_message(latest)
    # df_list = df.to_dict(orient="records")
    # print(df_list)

    # Risk:Reward Setup
    sl_distance = atr * 1.2  # ATR-based SL
    tp_distance = sl_distance * 2.5  # 1:2.5 Risk:Reward

    # Entry Conditions for LONG (BUY)
    if (
        prev["EMA_9"] < prev["EMA_21"] and latest["EMA_9"] > latest["EMA_21"]
        and latest["RSI"] > 50 and latest["close"] > latest["VWAP"]
    ):
        stop_loss = entry_price - sl_distance
        take_profit = entry_price + tp_distance
        return "buy", stop_loss, take_profit

    # Entry Conditions for SHORT (SELL)
    if (
        prev["EMA_9"] > prev["EMA_21"] and latest["EMA_9"] < latest["EMA_21"]
        and latest["RSI"] < 50 and latest["close"] < latest["VWAP"]
    ):
        stop_loss = entry_price + sl_distance
        take_profit = entry_price - tp_distance
        return "sell", stop_loss, take_profit

    return None, None, None
