# Financial Data Quality Sentinel

A real-time anomaly interception project for high-velocity financial market feeds.

## Stack
- Apache Kafka for streaming transport
- Python producer/consumer services
- Great Expectations for data quality checks
- PostgreSQL dual-sink persistence (clean + quarantine)
- Adminer for DB inspection
- Docker Compose for local orchestration

## Project layout
- `docker-compose.yml`: Kafka, Zookeeper, Postgres, Adminer
- `sql/init.sql`: table creation and indexes
- `app/producer.py`: yfinance poller -> Kafka topic
- `app/consumer.py`: Kafka consumer -> Great Expectations -> Postgres sinks
- `.env.example`: runtime configuration template

## Quick start
1. Copy env file:
   ```bash
   cp .env.example .env
   ```
2. Start infra:
   ```bash
   docker compose up -d
   ```
3. Install Python deps:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. Run producer:
   ```bash
   python app/producer.py
   ```
5. Run consumer:
   ```bash
   python app/consumer.py
   ```

## Validation rules
1. **Price > 0** to catch zero-out / null-like feed corruption.
2. **Absolute minute-over-minute change <= 20%** to catch fat-finger or flash anomalies.

Records that pass validation go to `clean_market_data`; failures go to `quarantine_logs` and optionally trigger Discord/Slack webhook alert.

## Example manual anomaly test
- Start producer and consumer.
- Publish a bad payload manually:
  ```bash
  docker exec -it $(docker ps -qf name=kafka) kafka-console-producer --broker-list localhost:9092 --topic market_ticks
  > {"symbol":"AAPL","price":0,"source_ts":"2026-04-30T12:00:00+00:00","provider":"manual"}
  ```
- Confirm row appears in `quarantine_logs` and alert is emitted.

## Phase mapping
- **Phase 1**: Infra + ingestion via `docker-compose.yml` and producer.
- **Phase 2**: Sentinel validation + dual-sink consumer.
- **Phase 3**: Webhook alerts + connect Power BI to Postgres for integrity dashboards.
- **Phase 4**: Portfolio packaging with diagram and scenario documentation.
