from kafka import KafkaConsumer
import json
import psycopg2

# Connect to Kafka
consumer = KafkaConsumer(
    'market_data',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Connect to Postgres
conn = psycopg2.connect(
    host="127.0.0.1",
    port=5433,
    database="postgres",
    user="postgres",
    password="postgres"
)

cursor = conn.cursor()

previous_price = None

for message in consumer:
    data = message.value
    symbol = data["symbol"]
    price = data["price"]

    print("Received:", data)

    percent_change = 0

    if previous_price:
        percent_change = ((price - previous_price) / previous_price) * 100

    # Validation rules
    if price <= 0:
        reason = "Price <= 0"
        cursor.execute(
            "INSERT INTO quarantine_logs (symbol, price, percent_change, reason) VALUES (%s, %s, %s, %s)",
            (symbol, price, percent_change, reason)
        )
        print("❌ Sent to quarantine:", reason)

    elif abs(percent_change) > 20:
        reason = "Change > 20%"
        cursor.execute(
            "INSERT INTO quarantine_logs (symbol, price, percent_change, reason) VALUES (%s, %s, %s, %s)",
            (symbol, price, percent_change, reason)
        )
        print("❌ Sent to quarantine:", reason)

    else:
        cursor.execute(
            "INSERT INTO clean_market_data (symbol, price, percent_change) VALUES (%s, %s, %s)",
            (symbol, price, percent_change)
        )
        print("✅ Stored clean data")

    conn.commit()
    previous_price = price
