# Function to determine whether to buy or sell based on strategy
from utils.logging_util import log_message
import requests
import json
import time
from config import BASE_URL,PRODUCT_SYMBOL


def get_historical_data(symbol='BTCUSD', resolution='5m', start=None, end=None):
    url = f"{BASE_URL}/v2/history/candles"
  
    # Default to the last 1 hour if no start time is provided
    if start is None:
        start = int(time.time()) - 86400  # 1 hour ago
    
    # Default to the current time if no end time is provided
    if end is None:
        end = int(time.time())  # Current time
    
    # Set the URL and headers for the request
    # url = 'https://api.india.delta.exchange/v2/history/candles'
    headers = {
        'Accept': 'application/json'
    }

    # Set the parameters for the GET request
    params = {
        'resolution': resolution,  # e.g., '5m' for 5-minute candles
        'symbol': symbol,          # e.g., 'BTCUSD' for Bitcoin/US Dollar
        'start': str(start),       # Start time in UNIX timestamp (seconds)
        'end': str(end)            # End time in UNIX timestamp (seconds)
    }
    
    # Send the GET request to fetch historical candles
    response = requests.get(url, params=params, headers=headers)
    # print(f"reponse",response.text)


    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # log_message(data)
        # log_message(data)
        
        # Check if the response contains the expected data
        if 'result' in data:
            return data['result']  # Return the historical candle data
        else:
            print("No data found for the given parameters.")
            return []
    else:
        print(f"Error fetching data: {response.status_code} - {response.text}")
        return []

# Function to calculate Exponential Moving Average (EMA)
def calculate_ema(prices, period):
    """
    Calculate the Exponential Moving Average (EMA).
    :param prices: List of closing prices.
    :param period: Period for the EMA.
    :return: EMA value.
    """
    if len(prices) < period:
        return None
    
    ema = sum(prices[-period:]) / period  # Simple initialization
    multiplier = 2 / (period + 1)
    for price in prices[-period:]:
        ema = (price - ema) * multiplier + ema
    return ema

# Function to calculate Relative Strength Index (RSI)
def calculate_rsi(prices, period=14):
    """
    Calculate the Relative Strength Index (RSI).
    :param prices: List of closing prices.
    :param period: Period for the RSI calculation.
    :return: RSI value.
    """
    if len(prices) < period:
        return None
    
    gains = 0
    losses = 0
    for i in range(1, period):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains += change
        else:
            losses -= change
    
    average_gain = gains / period
    average_loss = losses / period
    
    if average_loss == 0:
        return 100  # Avoid division by zero
    
    rs = average_gain / average_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def strategy_logic(PRODUCT_SYMBOL):
    """
    Implement the buying/selling strategy based on the 50 EMA and RSI.
    :return: String - 'buy' or 'sell', or None if no action.
    """
    # Fetch the latest historical data (50 candles for 5-minute timeframe)
    historical_data = get_historical_data(PRODUCT_SYMBOL, resolution="5m")
    if len(historical_data) < 50:
        log_message(historical_data)
        log_message("❌ Not enough data to make a decision.")
        return None
    
    closing_prices = [candle["close"] for candle in historical_data]

    # Calculate 50-period EMA and 14-period RSI
    ema_50 = calculate_ema(closing_prices, 50)
    rsi_14 = calculate_rsi(closing_prices, period=14)

    if ema_50 is None or rsi_14 is None:
        log_message("❌ Unable to calculate EMA or RSI.")
        return None
    
    log_message(f"✅ EMA(50): {ema_50}, RSI(14): {rsi_14}")

    # Entry Conditions:
    if closing_prices[-1] > ema_50 and rsi_14 > 50:
        log_message("✅ Bullish trend detected, RSI > 50. Buy signal!")
        return 'buy'
    elif closing_prices[-1] < ema_50 and rsi_14 < 50:
        log_message("✅ Bearish trend detected, RSI < 50. Sell signal!")
        return 'sell'
    else:
        log_message("❌ No clear signal.")
        return None