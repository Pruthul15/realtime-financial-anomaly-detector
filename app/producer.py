import time
import json
import random
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

symbol = "AAPL"
price = 271.35

while True:
    if random.random() < 0.2:
        send_price = price * random.uniform(3, 6)
        print("⚠️ Injecting anomaly...")
    else:
        send_price = price + random.uniform(-1, 1)

    message = {
        "symbol": symbol,
        "price": round(send_price, 2)
    }

    print("Sending:", message)
    producer.send("market_data", message)
    producer.flush()

    price = send_price
    time.sleep(5)