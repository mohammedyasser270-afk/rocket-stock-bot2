import os
import requests

API_KEY = os.environ["ALPACA_API_KEY"]
SECRET_KEY = os.environ["ALPACA_SECRET_KEY"]

url = "https://data.alpaca.markets/v2/stocks/PATH/trades/latest"

headers = {
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": SECRET_KEY,
}

response = requests.get(url, headers=headers, timeout=30)
response.raise_for_status()

data = response.json()
price = data["trade"]["p"]

print(f"PATH latest price: ${price}")
