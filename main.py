# main.py (Main script)
from utils.delta_api import place_order
from strategies.strategy import apply_indicators, check_trade_conditions
from utils.data_fetch import get_historical_data
import time

def run_bot():
    while True:
        df = get_historical_data("BTC/USD")
        df = apply_indicators(df)
        trade_signal = check_trade_conditions(df)
        if trade_signal == "BUY":
            print("Placing BUY order")
            place_order("BTC/USD", "buy", 5, 0.5, 2)
        elif trade_signal == "SELL":
            print("Placing SELL order")
            place_order("BTC/USD", "sell", 5, 0.5, 2)
        time.sleep(300)  # Run every 5 minutes

if __name__ == "__main__":
    run_bot()