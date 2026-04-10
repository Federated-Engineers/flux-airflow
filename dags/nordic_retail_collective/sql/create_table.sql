CREATE TABLE IF NOT EXISTS logistics (
    order_id VARCHAR(50),
    warehouse_origin VARCHAR(50),
    warehouse_zone VARCHAR(50),
    carrier VARCHAR(50),
    priority VARCHAR(50),
    is_disputed BOOLEAN,
    api_version VARCHAR(50),
    ingested_at TIMESTAMP,
    ingested_date DATE,
    ingested_year SMALLINT,
    ingested_month SMALLINT,
    ingested_day SMALLINT
);