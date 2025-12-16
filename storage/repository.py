# storage/repository.py
"""
SQLite repository for storing and retrieving network statistics.
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Dict

from models.data_models import InterfaceStat, FlowStat, HostStat, AppConfig, AlertRule
from storage.migrations import init_database, migrate_database


class Repository:
    """
    Data access layer for SQLite.
    Handles persistence of interface samples, flows, hosts, and configuration.
    """
    
    def __init__(self, db_path: Path = None):
        if db_path is None:
            db_path = Path.home() / ".network_monitor" / "data.db"
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize and migrate database
        migrate_database(self.db_path)
    
    def _get_conn(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    # ============ Interface Samples ============
    
    def save_interface_sample(self, stat: InterfaceStat) -> None:
        """Save a single interface sample."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO interface_samples
            (interface_name, timestamp, bytes_sent, bytes_recv, 
             packets_sent, packets_recv, rate_up_mbps, rate_down_mbps)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            stat.name,
            stat.timestamp,
            stat.bytes_sent,
            stat.bytes_recv,
            stat.packets_sent,
            stat.packets_recv,
            stat.rate_up_mbps,
            stat.rate_down_mbps
        ))
        
        conn.commit()
        conn.close()
    
    def save_interface_samples_batch(self, stats: Dict[str, InterfaceStat]) -> None:
        """Efficiently save multiple interface samples."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        data = [
            (stat.name, stat.timestamp, stat.bytes_sent, stat.bytes_recv,
             stat.packets_sent, stat.packets_recv, stat.rate_up_mbps, stat.rate_down_mbps)
            for stat in stats.values()
        ]
        
        cursor.executemany("""
            INSERT INTO interface_samples
            (interface_name, timestamp, bytes_sent, bytes_recv,
             packets_sent, packets_recv, rate_up_mbps, rate_down_mbps)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, data)
        
        conn.commit()
        conn.close()
    
    def get_interface_samples(self, interface_name: str, 
                             hours_back: int = 24) -> List[InterfaceStat]:
        """Get interface samples for a given time period."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cutoff = datetime.now() - timedelta(hours=hours_back)
        
        cursor.execute("""
            SELECT * FROM interface_samples
            WHERE interface_name = ? AND timestamp >= ?
            ORDER BY timestamp ASC
        """, (interface_name, cutoff))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            stat = InterfaceStat(
                name=row['interface_name'],
                bytes_sent=row['bytes_sent'],
                bytes_recv=row['bytes_recv'],
                packets_sent=row['packets_sent'],
                packets_recv=row['packets_recv'],
                rate_up_mbps=row['rate_up_mbps'],
                rate_down_mbps=row['rate_down_mbps'],
                timestamp=datetime.fromisoformat(row['timestamp'])
            )
            results.append(stat)
        
        return results
    
    # ============ Flows ============
    
    def save_flow(self, flow: FlowStat) -> None:
        """Save or update a flow session."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO flow_sessions
            (protocol, local_ip, local_port, remote_ip, remote_port,
             bytes_up, bytes_down, packets_up, packets_down,
             process_name, process_pid, start_time, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            flow.protocol.value,
            flow.local_ip,
            flow.local_port,
            flow.remote_ip,
            flow.remote_port,
            flow.bytes_up,
            flow.bytes_down,
            flow.packets_up,
            flow.packets_down,
            flow.process_name,
            flow.process_pid,
            flow.start_time,
            flow.last_seen
        ))
        
        conn.commit()
        conn.close()
    
    def save_flows_batch(self, flows: List[FlowStat]) -> None:
        """Save multiple flows efficiently."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        data = [
            (f.protocol.value, f.local_ip, f.local_port, f.remote_ip, f.remote_port,
             f.bytes_up, f.bytes_down, f.packets_up, f.packets_down,
             f.process_name, f.process_pid, f.start_time, f.last_seen)
            for f in flows
        ]
        
        cursor.executemany("""
            INSERT OR REPLACE INTO flow_sessions
            (protocol, local_ip, local_port, remote_ip, remote_port,
             bytes_up, bytes_down, packets_up, packets_down,
             process_name, process_pid, start_time, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data)
        
        conn.commit()
        conn.close()
    
    def get_active_flows(self, timeout_sec: int = 30) -> List[FlowStat]:
        """Get flows active in the last timeout_sec seconds."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(seconds=timeout_sec)).isoformat()
        
        cursor.execute("""
            SELECT * FROM flow_sessions
            WHERE last_seen >= ?
            ORDER BY bytes_up + bytes_down DESC
        """, (cutoff,))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            flow = FlowStat(
                protocol=row['protocol'],
                local_ip=row['local_ip'],
                local_port=row['local_port'],
                remote_ip=row['remote_ip'],
                remote_port=row['remote_port'],
                bytes_up=row['bytes_up'],
                bytes_down=row['bytes_down'],
                packets_up=row['packets_up'],
                packets_down=row['packets_down'],
                process_name=row['process_name'],
                process_pid=row['process_pid'],
                start_time=datetime.fromisoformat(row['start_time']),
                last_seen=datetime.fromisoformat(row['last_seen'])
            )
            results.append(flow)
        
        return results
    
    # ============ Hosts ============
    
    def save_host(self, host: HostStat) -> None:
        """Save or update a host stat."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO host_stats
            (ip, hostname, total_bytes_up, total_bytes_down,
             packets_up, packets_down, flow_count, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            host.ip,
            host.hostname,
            host.total_bytes_up,
            host.total_bytes_down,
            host.packets_up,
            host.packets_down,
            host.flow_count,
            host.last_seen
        ))
        
        conn.commit()
        conn.close()
    
    def get_top_hosts(self, limit: int = 10, hours_back: int = 24) -> List[HostStat]:
        """Get top hosts by total bytes transferred."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(hours=hours_back)).isoformat()
        
        cursor.execute("""
            SELECT * FROM host_stats
            WHERE last_seen >= ?
            ORDER BY (total_bytes_up + total_bytes_down) DESC
            LIMIT ?
        """, (cutoff, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            host = HostStat(
                ip=row['ip'],
                hostname=row['hostname'],
                total_bytes_up=row['total_bytes_up'],
                total_bytes_down=row['total_bytes_down'],
                packets_up=row['packets_up'],
                packets_down=row['packets_down'],
                flow_count=row['flow_count'],
                last_seen=datetime.fromisoformat(row['last_seen'])
            )
            results.append(host)
        
        return results
    
    # ============ Configuration ============
    
    def get_config(self) -> AppConfig:
        """Get application configuration."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM app_config WHERE id = 1")
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return AppConfig()
        
        interface_list = []
        if row['interface_selection']:
            interface_list = row['interface_selection'].split(',')
        
        return AppConfig(
            sampling_interval_ms=row['sampling_interval_ms'],
            retention_days=row['retention_days'],
            deep_capture_enabled=bool(row['deep_capture_enabled']),
            interface_selection=interface_list,
            privacy_no_hostname=bool(row['privacy_no_hostname']),
            privacy_limit_retention=bool(row['privacy_limit_retention']),
            chart_history_seconds=row['chart_history_seconds']
        )
    
    def save_config(self, config: AppConfig) -> None:
        """Save application configuration."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        interface_str = ','.join(config.interface_selection) if config.interface_selection else ''
        
        cursor.execute("""
            UPDATE app_config SET
                sampling_interval_ms = ?,
                retention_days = ?,
                deep_capture_enabled = ?,
                interface_selection = ?,
                privacy_no_hostname = ?,
                privacy_limit_retention = ?,
                chart_history_seconds = ?
            WHERE id = 1
        """, (
            config.sampling_interval_ms,
            config.retention_days,
            int(config.deep_capture_enabled),
            interface_str,
            int(config.privacy_no_hostname),
            int(config.privacy_limit_retention),
            config.chart_history_seconds
        ))
        
        conn.commit()
        conn.close()
    
    # ============ Cleanup ============
    
    def cleanup_old_data(self, retention_days: int = 30) -> None:
        """
        Delete interface samples and flows older than retention_days.
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(days=retention_days)).isoformat()
        
        cursor.execute("""
            DELETE FROM interface_samples
            WHERE timestamp < ?
        """, (cutoff,))
        
        cursor.execute("""
            DELETE FROM flow_sessions
            WHERE last_seen < ?
        """, (cutoff,))
        
        cursor.execute("""
            DELETE FROM host_stats
            WHERE last_seen < ?
        """, (cutoff,))
        
        conn.commit()
        conn.close()
