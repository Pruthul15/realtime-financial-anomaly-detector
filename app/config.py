from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    kafka_bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    kafka_topic: str = os.getenv("KAFKA_TOPIC", "market_ticks")
    kafka_group_id: str = os.getenv("KAFKA_GROUP_ID", "sentinel-consumer")
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    postgres_db: str = os.getenv("POSTGRES_DB", "market_sentinel")
    postgres_user: str = os.getenv("POSTGRES_USER", "postgres")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    symbols: tuple[str, ...] = tuple(s.strip() for s in os.getenv("SYMBOLS", "AAPL,MSFT").split(","))
    poll_seconds: int = int(os.getenv("POLL_SECONDS", "60"))
    alert_webhook_url: str = os.getenv("ALERT_WEBHOOK_URL", "")


settings = Settings()
