import requests
import json

url = "https://cdn-ind.testnet.deltaex.org"
response = requests.get(url)
contracts = response.json()

for product in contracts['result']:
    print(product['symbol'], "-", product['id'])
