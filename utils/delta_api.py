# utils/delta_api.py

import time
import hmac
import hashlib
import requests
import json
from config import API_KEY, API_SECRET, BASE_URL
from utils.logging_util import log_message

def generate_signature(method, endpoint, body):
    """
    Generate HMAC SHA256 signature for Delta Exchange API.
    """
    timestamp = str(int(time.time()))
    message = method + timestamp + endpoint + body
    signature = hmac.new(API_SECRET.encode(), message.encode(), hashlib.sha256).hexdigest()
    return signature, timestamp




# Function to get the latest price of a product
def get_latest_price(product_id='BTCUSD'):
    url = f"{BASE_URL}/v2/tickers/BTCUSD"
    response = requests.get(url)
    
    print("🔹 API Response Status:", response.status_code)  # ✅ Check status code
    # print("🔹 API Raw Response:", response.text)  # ✅ Print raw response

    if response.status_code != 200:
        raise Exception(f"⚠️ API Error: {response.status_code} {response.text}")

    try:
        data = response.json()
        # log_message(data['result']['close'])
        return float(data['result']['close'])  # ✅ Latest closing price
    except json.JSONDecodeError:
        raise Exception("❌ JSON Decode Error: API returned invalid JSON.")



def place_order(product_id, size, side,trigger_method="last_traded_price"):
    """
    Place a market order on Delta Exchange.
    """
    endpoint = "/v2/orders"
    url = BASE_URL + endpoint
    method = "POST"
    body = json.dumps({
        "product_symbol": "BTCUSD",
        "size": size,
        "side": side,
        "order_type": "market_order"
    })

    signature, timestamp = generate_signature(method, endpoint, body)

    headers = {
        "api-key": API_KEY,
        "signature": signature,
        "timestamp": timestamp,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, data=body)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


   
def place_bracket_order(product_symbol, size, side,sl,tp, trigger_method="last_traded_price"):

     # Fetch latest price
    # entry_price = get_latest_price(product_id)
    stop_loss = sl
    take_profit = tp



    endpoint = "/v2/orders/bracket"
    url = BASE_URL + endpoint
    method = "POST"
    body = json.dumps({
          "product_symbol": product_symbol,  # Symbol for the product (BTCUSD)
        "size": size,  # Order size
        "side": side,  # Side (buy/sell)
        "order_type": "market_order",  # Main market order
        "bracket_stop_trigger_method": trigger_method,  # Trigger method for stop-loss and take-profit
        "stop_loss_order": {
            "order_type": "limit_order",  # Stop-Loss order as limit order
            "stop_price": str(stop_loss),  # Stop-Loss price
            "limit_price": str(stop_loss - 50)  # Limit price for stop loss (50 points below stop price)
        },
        "take_profit_order": {
            "order_type": "limit_order",  # Take-Profit order as limit order
            "stop_price": str(take_profit),  # Take-Profit stop price
            "limit_price": str(take_profit - 50)  # Limit price for take profit (50 points below stop price)
        }
    })

    signature, timestamp = generate_signature(method, endpoint, body)

    headers = {
        "api-key": API_KEY,
        "signature": signature,
        "timestamp": timestamp,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, data=body)
        log_message(response.text)

        return response.json()
    except Exception as e:
        return {"error": str(e)}
   

 

