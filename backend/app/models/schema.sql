-- Consumer Attention Mapping System
-- Fresh-install schema for PostgreSQL + TimescaleDB.
-- Existing installations should run app/migrations/001_platform_completion.sql.

CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

INSERT INTO roles (id, role_name, description) VALUES
(1, 'SuperAdmin', 'Platform administrator'),
(2, 'StoreManager', 'Store operations'),
(3, 'RetailAnalyst', 'Retail analytics')
ON CONFLICT (role_name) DO NOTHING;

SELECT setval('roles_id_seq', GREATEST((SELECT COALESCE(MAX(id), 1) FROM roles), 1), true);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role_id INT NOT NULL REFERENCES roles(id) ON DELETE RESTRICT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS store_zones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    store_id UUID NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    roi_polygon JSONB NOT NULL DEFAULT '[]'::jsonb,
    bbox JSONB,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cameras (
    id VARCHAR(100) PRIMARY KEY,
    store_id UUID NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    zone_id UUID REFERENCES store_zones(id) ON DELETE SET NULL,
    camera_name VARCHAR(150),
    rtsp_url TEXT,
    source_type VARCHAR(30) NOT NULL DEFAULT 'rtsp',
    source_url TEXT,
    video_path TEXT,
    fps INT NOT NULL DEFAULT 30,
    resolution VARCHAR(30) NOT NULL DEFAULT '1920x1080',
    status VARCHAR(30) NOT NULL DEFAULT 'offline',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS shelves (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    store_id UUID NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    zone_id UUID REFERENCES store_zones(id) ON DELETE SET NULL,
    camera_id VARCHAR(100) REFERENCES cameras(id) ON DELETE SET NULL,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(100),
    tier_count INT NOT NULL DEFAULT 1,
    roi_polygon JSONB NOT NULL,
    bbox JSONB,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

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
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_product_camera_mapping UNIQUE(product_id, shelf_id, camera_id)
);

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

CREATE TABLE IF NOT EXISTS product_attention_metrics (
    product_id UUID PRIMARY KEY REFERENCES products(id) ON DELETE CASCADE,
    store_id UUID REFERENCES stores(id) ON DELETE SET NULL,
    zone_id UUID REFERENCES store_zones(id) ON DELETE SET NULL,
    shelf_id UUID REFERENCES shelves(id) ON DELETE SET NULL,
    camera_id VARCHAR(100) REFERENCES cameras(id) ON DELETE SET NULL,
    sku VARCHAR(100),
    product_name VARCHAR(255) NOT NULL DEFAULT 'Unnamed product',
    category VARCHAR(100),
    brand VARCHAR(100),
    tier INT NOT NULL DEFAULT 1,
    confidence DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    roi_polygon JSONB NOT NULL DEFAULT '[]'::jsonb,
    attention_duration DOUBLE PRECISION NOT NULL DEFAULT 0,
    interaction_frequency INT NOT NULL DEFAULT 0,
    pickup_rate DOUBLE PRECISION NOT NULL DEFAULT 0 CHECK (pickup_rate BETWEEN 0 AND 1),
    conversion_rate DOUBLE PRECISION NOT NULL DEFAULT 0 CHECK (conversion_rate BETWEEN 0 AND 1),
    repeat_engagement INT NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS shopper_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INT REFERENCES users(id) ON DELETE SET NULL,
    store_id UUID NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    path_length DOUBLE PRECISION NOT NULL DEFAULT 0,
    total_dwell_time DOUBLE PRECISION NOT NULL DEFAULT 0,
    head_gaze_shifts INT NOT NULL DEFAULT 0,
    behavioral_segment VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

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
    dwell_time_seconds DOUBLE PRECISION NOT NULL CHECK (dwell_time_seconds >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_attention_time CHECK (exit_time >= entry_time)
);

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

CREATE TABLE IF NOT EXISTS shopper_dwell_analytics (
    time TIMESTAMPTZ NOT NULL,
    store_id UUID NOT NULL REFERENCES stores(id),
    zone_id UUID REFERENCES store_zones(id),
    camera_id VARCHAR(100) REFERENCES cameras(id),
    shelf_id UUID REFERENCES shelves(id),
    shopper_id INT NOT NULL,
    dwell_seconds DOUBLE PRECISION NOT NULL CHECK (dwell_seconds >= 0)
);

SELECT create_hypertable('shopper_dwell_analytics', 'time', if_not_exists => TRUE);

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

CREATE INDEX IF NOT EXISTS idx_zone_store ON store_zones(store_id);
CREATE INDEX IF NOT EXISTS idx_camera_store ON cameras(store_id);
CREATE INDEX IF NOT EXISTS idx_camera_zone ON cameras(zone_id);
CREATE INDEX IF NOT EXISTS idx_shelf_store ON shelves(store_id);
CREATE INDEX IF NOT EXISTS idx_shelf_zone ON shelves(zone_id);
CREATE INDEX IF NOT EXISTS idx_shelf_camera ON shelves(camera_id);
CREATE INDEX IF NOT EXISTS idx_shelf_roi ON shelves USING GIN(roi_polygon);
CREATE INDEX IF NOT EXISTS idx_product_store ON products(store_id);
CREATE INDEX IF NOT EXISTS idx_product_shelf ON products(shelf_id);
CREATE INDEX IF NOT EXISTS idx_product_camera ON products(camera_id);
CREATE INDEX IF NOT EXISTS idx_product_mapping_product ON product_mappings(product_id);
CREATE INDEX IF NOT EXISTS idx_product_mapping_camera ON product_mappings(camera_id);
CREATE INDEX IF NOT EXISTS idx_attention_store ON attention_sessions(store_id, entry_time DESC);
CREATE INDEX IF NOT EXISTS idx_attention_camera ON attention_sessions(camera_id);
CREATE INDEX IF NOT EXISTS idx_attention_shelf ON attention_sessions(shelf_id);
CREATE INDEX IF NOT EXISTS idx_tracking_store_time ON tracking_points(store_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_tracking_camera_time ON tracking_points(camera_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_dwell_store ON shopper_dwell_analytics(store_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_dwell_zone ON shopper_dwell_analytics(zone_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_dwell_camera ON shopper_dwell_analytics(camera_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_dwell_shelf ON shopper_dwell_analytics(shelf_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_alert_store_created ON alerts(store_id, created_at DESC);
