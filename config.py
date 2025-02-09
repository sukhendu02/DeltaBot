# config.py

# API Credentials (Replace with your actual Delta Exchange API key and secret)
API_KEY = "zbPKFbceoXpT0TQdMpNiU93KnkmXZa"
API_SECRET = "I65n9LbcABGcTw2acXuhQPBXvsDT1S6mWsRRAFd0WNKSJh5IG54mOsTm1GoA"

TELEGRAM_BOT_TOKEN="7561327864:AAFIpawogTeq2bPEgOEKOK16Mj_xCHAuRw0"
TELEGRAM_CHAT_ID="646886449"

# Delta Exchange Base URL
BASE_URL = "https://cdn-ind.testnet.deltaex.org"

# Default product ID (BTC/USD perpetual contract)
PRODUCT_ID = 27  # Replace with the correct product ID if needed
PRODUCT_SYMBOL="BTCUSD"


TRADE_AMOUNT=5
LEVERAGE=25
ORDER_SIZE=1


# strategy parameters
EMA_SHORT = 9
EMA_LONG = 21
SUPER_TREND_PERIOD = 10
SUPER_TREND_MULTIPLIER = 3

CANDLE_URL="https://api.india.delta.exchange/v2/history/candles"

WEBHOOKURL="https://cdn-ind.testnet.deltaex.org/v2/webhook_alert/27a2507ac348605615d438dac54fbecb"