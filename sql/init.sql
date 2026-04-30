CREATE TABLE IF NOT EXISTS clean_market_data (
    id BIGSERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    price NUMERIC(18, 8) NOT NULL,
    percent_change NUMERIC(10, 4) NOT NULL,
    source_ts TIMESTAMPTZ NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS quarantine_logs (
    id BIGSERIAL PRIMARY KEY,
    symbol TEXT,
    price NUMERIC(18, 8),
    source_ts TIMESTAMPTZ,
    payload JSONB NOT NULL,
    validation_errors JSONB NOT NULL,
    quarantined_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_clean_market_data_symbol_ts
    ON clean_market_data(symbol, source_ts DESC);

CREATE INDEX IF NOT EXISTS idx_quarantine_logs_symbol_ts
    ON quarantine_logs(symbol, source_ts DESC);
