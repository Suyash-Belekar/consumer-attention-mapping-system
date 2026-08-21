-- Idempotent migration for the CAMS mapping/tracking/product platform.
-- Safe to run against the existing consumer_analytics database.

CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

ALTER TABLE store_zones ADD COLUMN IF NOT EXISTS roi_polygon JSONB NOT NULL DEFAULT '[]'::jsonb;
ALTER TABLE store_zones ADD COLUMN IF NOT EXISTS bbox JSONB;
ALTER TABLE store_zones ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE store_zones ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

ALTER TABLE cameras ADD COLUMN IF NOT EXISTS camera_name VARCHAR(150);
ALTER TABLE cameras ADD COLUMN IF NOT EXISTS video_path TEXT;
ALTER TABLE cameras ADD COLUMN IF NOT EXISTS status VARCHAR(30) NOT NULL DEFAULT 'offline';
ALTER TABLE cameras ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

UPDATE cameras SET camera_name = id WHERE camera_name IS NULL;

CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    store_id UUID NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    zone_id UUID REFERENCES store_zones(id) ON DELETE SET NULL,
    shelf_id UUID REFERENCES shelves(id) ON DELETE SET NULL,
    camera_id VARCHAR(100) REFERENCES cameras(id) ON DELETE SET NULL,
    name VARCHAR(200) NOT NULL,
    sku VARCHAR(100),
    brand VARCHAR(100),
    category VARCHAR(100),
    unit_price DOUBLE PRECISION,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_products_store ON products(store_id);
CREATE INDEX IF NOT EXISTS idx_products_shelf ON products(shelf_id);
CREATE INDEX IF NOT EXISTS idx_products_camera ON products(camera_id);

CREATE TABLE IF NOT EXISTS attention_sessions (
    id BIGSERIAL PRIMARY KEY,
    tracker_id INT NOT NULL,
    store_id UUID REFERENCES stores(id) ON DELETE SET NULL,
    zone_id UUID REFERENCES store_zones(id) ON DELETE SET NULL,
    camera_id VARCHAR(100) REFERENCES cameras(id) ON DELETE SET NULL,
    shelf_id UUID REFERENCES shelves(id) ON DELETE SET NULL,
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,
    entry_time TIMESTAMPTZ NOT NULL,
    exit_time TIMESTAMPTZ NOT NULL,
    dwell_time_seconds DOUBLE PRECISION NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS product_mappings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    store_id UUID NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    shelf_id UUID NOT NULL REFERENCES shelves(id) ON DELETE CASCADE,
    camera_id VARCHAR(100) REFERENCES cameras(id) ON DELETE SET NULL,
    roi_polygon JSONB NOT NULL,
    bbox JSONB,
    tier INT NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_product_mapping_product ON product_mappings(product_id);
CREATE INDEX IF NOT EXISTS idx_product_mapping_camera ON product_mappings(camera_id);
CREATE INDEX IF NOT EXISTS idx_product_mapping_shelf ON product_mappings(shelf_id);

CREATE TABLE IF NOT EXISTS camera_zone_mappings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    camera_id VARCHAR(100) NOT NULL REFERENCES cameras(id) ON DELETE CASCADE,
    zone_id UUID NOT NULL REFERENCES store_zones(id) ON DELETE CASCADE,
    roi_polygon JSONB NOT NULL,
    bbox JSONB,
    calibration JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_camera_zone_mapping UNIQUE(camera_id, zone_id)
);

CREATE INDEX IF NOT EXISTS idx_camera_zone_mapping_camera ON camera_zone_mappings(camera_id);
CREATE INDEX IF NOT EXISTS idx_camera_zone_mapping_zone ON camera_zone_mappings(zone_id);

CREATE TABLE IF NOT EXISTS camera_shelf_mappings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    camera_id VARCHAR(100) NOT NULL REFERENCES cameras(id) ON DELETE CASCADE,
    shelf_id UUID NOT NULL REFERENCES shelves(id) ON DELETE CASCADE,
    roi_polygon JSONB NOT NULL,
    bbox JSONB,
    calibration JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_camera_shelf_mapping UNIQUE(camera_id, shelf_id)
);

CREATE INDEX IF NOT EXISTS idx_camera_shelf_mapping_camera ON camera_shelf_mappings(camera_id);
CREATE INDEX IF NOT EXISTS idx_camera_shelf_mapping_shelf ON camera_shelf_mappings(shelf_id);

CREATE TABLE IF NOT EXISTS tracking_points (
    id BIGSERIAL PRIMARY KEY,
    store_id UUID NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    camera_id VARCHAR(100) REFERENCES cameras(id) ON DELETE SET NULL,
    zone_id UUID REFERENCES store_zones(id) ON DELETE SET NULL,
    shelf_id UUID REFERENCES shelves(id) ON DELETE SET NULL,
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,
    tracker_id INT NOT NULL,
    x DOUBLE PRECISION NOT NULL,
    y DOUBLE PRECISION NOT NULL,
    value DOUBLE PRECISION NOT NULL DEFAULT 1,
    timestamp TIMESTAMPTZ NOT NULL
);

ALTER TABLE tracking_points ADD COLUMN IF NOT EXISTS product_id UUID REFERENCES products(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_tracking_store_time ON tracking_points(store_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_tracking_camera_time ON tracking_points(camera_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_tracking_tracker_time ON tracking_points(tracker_id, timestamp DESC);

CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    store_id UUID NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    alert_type VARCHAR(80) NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alert_store_created ON alerts(store_id, created_at DESC);

-- Link metrics to product IDs when possible without rewriting existing rows.
CREATE INDEX IF NOT EXISTS idx_product_metrics_store ON product_attention_metrics(store_id);
CREATE INDEX IF NOT EXISTS idx_product_metrics_shelf ON product_attention_metrics(shelf_id);

-- Existing installations may already have attention_sessions from schema.sql.
-- Keep this additive and idempotent.
ALTER TABLE attention_sessions ADD COLUMN IF NOT EXISTS product_id UUID REFERENCES products(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS idx_attention_product ON attention_sessions(product_id);

-- TimescaleDB Hypertables: ensure composite primary keys and convert time-series tables
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM timescaledb_information.hypertables WHERE hypertable_name = 'tracking_points'
    ) THEN
        ALTER TABLE tracking_points DROP CONSTRAINT IF EXISTS tracking_points_pkey;
        ALTER TABLE tracking_points ADD PRIMARY KEY (id, timestamp);
        PERFORM create_hypertable('tracking_points', 'timestamp', if_not_exists => TRUE, migrate_data => TRUE);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM timescaledb_information.hypertables WHERE hypertable_name = 'attention_sessions'
    ) THEN
        ALTER TABLE attention_sessions DROP CONSTRAINT IF EXISTS attention_sessions_pkey;
        ALTER TABLE attention_sessions ADD PRIMARY KEY (id, entry_time);
        PERFORM create_hypertable('attention_sessions', 'entry_time', if_not_exists => TRUE, migrate_data => TRUE);
    END IF;
END $$;

