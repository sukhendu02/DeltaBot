# bot.py

import time
from utils.delta_api import place_order, place_bracket_order
from utils.logging_util import log_message
from config import PRODUCT_ID, ORDER_SIZE,PRODUCT_SYMBOL
from strategies.strategy2 import strategy_logic
from utils.telegram import send_telegram_message

def main():
    # order_size = 1  # Adjust as needed
    while True:

        log_message("🕑 Checking for new trade opportunity...")

        # Step 1: Check strategy logic (buy or sell signal)
        order_type,sl,tp = strategy_logic(PRODUCT_SYMBOL)
        log_message(order_type)
        log_message(sl)
        log_message(tp)




        # Step 1: Place a market buy order
        if order_type == "buy":

            log_message("🔵 Placing market BUY order...")
            buy_order = place_order(PRODUCT_SYMBOL, ORDER_SIZE, "buy")
            log_message(f"✅ Buy order response: {buy_order}")

            if buy_order.get('success', False):

                # Step 2: Place Bracket Order (Stop-Loss & Take-Profit) if Market Order is successful
                log_message("Placing bracket order")
                bracket_order_response = place_bracket_order(PRODUCT_SYMBOL, ORDER_SIZE, "buy",sl,tp)
                print("Bracket Order Response:", bracket_order_response)

            else:
                print("❌ Failed to place market order. Cannot place bracket order.")

            if "error" in buy_order:
                log_message("❌ Order placement failed.")
                message = f"❌ *Order Placement Failed!* "
                send_telegram_message(message)
                return
            message = f"✅ *Buy Order Placed!* \n🎯 Entry Price: {buy_order['result']['average_fill_price']}\n🔹 Quantity: "
            send_telegram_message(message)

            
            
            

        if order_type == "sell":

            log_message("🔵 Placing market BUY order...")
            sell_order = place_order(PRODUCT_SYMBOL, ORDER_SIZE, order_type)
            log_message(f"✅ Buy order response: {sell_order}")

            if sell_order.get('success', False):

                # Step 2: Place Bracket Order (Stop-Loss & Take-Profit) if Market Order is successful
                log_message("Placing bracket order")
                bracket_order_response = place_bracket_order(PRODUCT_SYMBOL, ORDER_SIZE, order_type,sl,tp)
                print("Bracket Order Response:", bracket_order_response)
            else:
                print("❌ Failed to place market order. Cannot place bracket order.")

            if "error" in sell_order:
                log_message("❌ Order placement failed.")
                message = f"❌ *Order Placement Failed!* "
                send_telegram_message(message)
                return
            message = f"🔴 *Sell Order Placed!* \n💰"
            send_telegram_message(message)
            
        # elif order_type == 'sell':
        #     log_message("🔴 Placing market SELL order...")
        #     sell_order = place_order(PRODUCT_ID, order_size, "sell")
        #     log_message(f"✅ Sell order response: {sell_order}")

        #     if sell_order.get('success', False):
        #         log_message("Placing bracket order...")
        #         bracket_order_response = place_bracket_order(PRODUCT_ID, order_size, "sell")
        #         print("Bracket Order Response:", bracket_order_response)
        #     else:
        #         log_message("❌ Failed to place market sell order.")
    # Step 2: Wait for 30 seconds
        time.sleep(60)

    # Step 3: Place a market sell order to close the position
    # log_message("🔴 Placing market SELL order...")
    # sell_order = place_order(PRODUCT_ID, order_size, "sell")
    # log_message(f"✅ Sell order response: {sell_order}")

if __name__ == "__main__":
    main()
