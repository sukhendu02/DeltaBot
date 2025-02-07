# bot.py

import time
from utils.delta_api import place_order, place_bracket_order
from utils.logging_util import log_message
from config import PRODUCT_ID
from utils.telegram import send_telegram_message

def main():
    order_size = 1  # Adjust as needed

    # Step 1: Place a market buy order
    log_message("🔵 Placing market BUY order...")
    buy_order = place_order(PRODUCT_ID, order_size, "sell")
    log_message(f"✅ Buy order response: {buy_order}")

    if buy_order.get('success', False):
        # Step 2: Place Bracket Order (Stop-Loss & Take-Profit) if Market Order is successful
        log_message("Placing bracket order")
        bracket_order_response = place_bracket_order(PRODUCT_ID, order_size, "sell")
        print("Bracket Order Response:", bracket_order_response)
    else:
        print("❌ Failed to place market order. Cannot place bracket order.")

    if "error" in buy_order:
        log_message("❌ Order placement failed.")
        return
    
    message = f"✅ *Buy Order Placed!* \n🎯 Entry Price: {buy_order['result']['average_fill_price']}\n🔹 Quantity: {order_size}"
    send_telegram_message(message)

    # Step 2: Wait for 30 seconds
    # time.sleep(30)

    # Step 3: Place a market sell order to close the position
    # log_message("🔴 Placing market SELL order...")
    # sell_order = place_order(PRODUCT_ID, order_size, "sell")
    # log_message(f"✅ Sell order response: {sell_order}")

if __name__ == "__main__":
    main()
