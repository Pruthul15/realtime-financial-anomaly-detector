import time
import json
from kafka import KafkaProducer
import yfinance as yf

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

symbol = "AAPL"

while True:
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d", interval="1m")

        if not data.empty:
            latest = data.tail(1).iloc[0]

            message = {
                "symbol": symbol,
                "price": float(latest["Close"]),
            }

            print("Sending:", message)
            producer.send("market_data", message)

        # 🔥 IMPORTANT: slow down requests
        time.sleep(90)

    except Exception as e:
        print("Error:", e)
        print("Sleeping to avoid rate limit...")
        time.sleep(120)