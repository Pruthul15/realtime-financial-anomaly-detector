import json
from datetime import datetime

import great_expectations as gx
import psycopg
import requests
from confluent_kafka import Consumer

from config import settings


def send_alert(message: str) -> None:
    if not settings.alert_webhook_url:
        return
    requests.post(settings.alert_webhook_url, json={"content": message}, timeout=5)


def validate_record(record: dict, previous_price: float | None) -> list[str]:
    errors: list[str] = []

    ge_df = gx.from_pandas(
        __import__("pandas").DataFrame([{"price": record["price"]}])
    )
    result = ge_df.expect_column_values_to_be_between("price", min_value=0.00000001)
    if not result.success:
        errors.append("Price must be greater than zero")

    if previous_price is not None:
        pct_change = ((record["price"] - previous_price) / previous_price) * 100
        record["percent_change"] = pct_change
        if abs(pct_change) > 20:
            errors.append(f"Percent change breached threshold: {pct_change:.2f}%")
    else:
        record["percent_change"] = 0.0

    return errors


def main() -> None:
    consumer = Consumer(
        {
            "bootstrap.servers": settings.kafka_bootstrap_servers,
            "group.id": settings.kafka_group_id,
            "auto.offset.reset": "earliest",
        }
    )
    consumer.subscribe([settings.kafka_topic])

    conn = psycopg.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        dbname=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password,
    )
    previous_by_symbol: dict[str, float] = {}

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None or msg.error():
                continue

            record = json.loads(msg.value().decode("utf-8"))
            symbol = record["symbol"]
            previous = previous_by_symbol.get(symbol)
            errors = validate_record(record, previous)

            with conn.cursor() as cur:
                if errors:
                    cur.execute(
                        """
                        INSERT INTO quarantine_logs (symbol, price, source_ts, payload, validation_errors)
                        VALUES (%s, %s, %s, %s::jsonb, %s::jsonb)
                        """,
                        (
                            symbol,
                            record["price"],
                            datetime.fromisoformat(record["source_ts"]),
                            json.dumps(record),
                            json.dumps(errors),
                        ),
                    )
                    send_alert(f"🚨 Quarantined {symbol}: {'; '.join(errors)}")
                else:
                    cur.execute(
                        """
                        INSERT INTO clean_market_data (symbol, price, percent_change, source_ts)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (
                            symbol,
                            record["price"],
                            record["percent_change"],
                            datetime.fromisoformat(record["source_ts"]),
                        ),
                    )
                    previous_by_symbol[symbol] = record["price"]
            conn.commit()
    finally:
        consumer.close()
        conn.close()


if __name__ == "__main__":
    main()
