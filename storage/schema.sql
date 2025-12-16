-- storage/schema.sql
-- SQLite schema for network monitoring application

-- Schema version tracking for migrations
CREATE TABLE IF NOT EXISTS schema_version (
    id INTEGER PRIMARY KEY,
    version INTEGER NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Interface samples (time-series data)
CREATE TABLE IF NOT EXISTS interface_samples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interface_name TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    bytes_sent INTEGER NOT NULL DEFAULT 0,
    bytes_recv INTEGER NOT NULL DEFAULT 0,
    packets_sent INTEGER NOT NULL DEFAULT 0,
    packets_recv INTEGER NOT NULL DEFAULT 0,
    rate_up_mbps REAL DEFAULT 0.0,
    rate_down_mbps REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_interface_samples_iface_time 
    ON interface_samples(interface_name, timestamp DESC);

-- Flow sessions (active and historical)
CREATE TABLE IF NOT EXISTS flow_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    protocol TEXT NOT NULL,
    local_ip TEXT NOT NULL,
    local_port INTEGER NOT NULL,
    remote_ip TEXT NOT NULL,
    remote_port INTEGER NOT NULL,
    bytes_up INTEGER NOT NULL DEFAULT 0,
    bytes_down INTEGER NOT NULL DEFAULT 0,
    packets_up INTEGER NOT NULL DEFAULT 0,
    packets_down INTEGER NOT NULL DEFAULT 0,
    process_name TEXT,
    process_pid INTEGER,
    start_time TIMESTAMP NOT NULL,
    last_seen TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_flow_5tuple 
    ON flow_sessions(protocol, local_ip, local_port, remote_ip, remote_port);

CREATE INDEX IF NOT EXISTS idx_flow_sessions_remote_ip 
    ON flow_sessions(remote_ip);

CREATE INDEX IF NOT EXISTS idx_flow_sessions_last_seen 
    ON flow_sessions(last_seen DESC);

-- Host aggregates
CREATE TABLE IF NOT EXISTS host_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT UNIQUE NOT NULL,
    hostname TEXT,
    total_bytes_up INTEGER NOT NULL DEFAULT 0,
    total_bytes_down INTEGER NOT NULL DEFAULT 0,
    packets_up INTEGER NOT NULL DEFAULT 0,
    packets_down INTEGER NOT NULL DEFAULT 0,
    flow_count INTEGER DEFAULT 0,
    last_seen TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_host_stats_last_seen 
    ON host_stats(last_seen DESC);

-- Alert rules
CREATE TABLE IF NOT EXISTS alert_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    metric TEXT NOT NULL,
    operator TEXT NOT NULL,
    threshold REAL NOT NULL,
    duration_seconds INTEGER DEFAULT 10,
    enabled INTEGER DEFAULT 1,
    interface_filter TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Alert triggers (log of when alerts fire)
CREATE TABLE IF NOT EXISTS alert_triggers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_rule_id INTEGER NOT NULL,
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    interface_name TEXT,
    value REAL NOT NULL,
    FOREIGN KEY(alert_rule_id) REFERENCES alert_rules(id)
);

CREATE INDEX IF NOT EXISTS idx_alert_triggers_timestamp 
    ON alert_triggers(triggered_at DESC);

-- Application configuration
CREATE TABLE IF NOT EXISTS app_config (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    sampling_interval_ms INTEGER DEFAULT 1000,
    retention_days INTEGER DEFAULT 30,
    deep_capture_enabled INTEGER DEFAULT 0,
    interface_selection TEXT,
    privacy_no_hostname INTEGER DEFAULT 0,
    privacy_limit_retention INTEGER DEFAULT 1,
    chart_history_seconds INTEGER DEFAULT 300,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default config row
INSERT OR IGNORE INTO app_config (id) VALUES (1);
