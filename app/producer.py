import json
import time
from datetime import datetime, timezone

import yfinance as yf
from confluent_kafka import Producer

from config import settings


def fetch_prices(symbols: tuple[str, ...]) -> list[dict]:
    payloads: list[dict] = []
    for symbol in symbols:
        ticker = yf.Ticker(symbol)
        try:
            latest = ticker.fast_info.last_price
        except Exception:
            latest = None
        if latest is None:
            continue
        payloads.append(
            {
                "symbol": symbol,
                "price": float(latest),
                "source_ts": datetime.now(timezone.utc).isoformat(),
                "provider": "yfinance",
            }
        )
    return payloads


def main() -> None:
    producer = Producer({"bootstrap.servers": settings.kafka_bootstrap_servers})

    while True:
        records = fetch_prices(settings.symbols)
        for record in records:
            producer.produce(
                settings.kafka_topic,
                key=record["symbol"],
                value=json.dumps(record).encode("utf-8"),
            )
        producer.flush()
        print(f"Published {len(records)} tick(s) at {datetime.now(timezone.utc).isoformat()}")
        time.sleep(settings.poll_seconds)


if __name__ == "__main__":
    main()

