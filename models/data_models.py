# models/data_models.py
"""
Data models for network monitoring.
Uses dataclasses for type safety and clarity.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class Protocol(str, Enum):
    """Protocol enumeration."""
    TCP = "TCP"
    UDP = "UDP"
    ICMP = "ICMP"
    OTHER = "OTHER"


@dataclass
class InterfaceStat:
    """Represents statistics for a single network interface."""
    name: str
    bytes_sent: int = 0
    bytes_recv: int = 0
    packets_sent: int = 0
    packets_recv: int = 0
    rate_up_mbps: float = 0.0  # Current upload rate in Mbps
    rate_down_mbps: float = 0.0  # Current download rate in Mbps
    is_up: bool = True
    timestamp: datetime = field(default_factory=datetime.now)
    
    def total_bytes(self) -> int:
        """Total bytes transferred."""
        return self.bytes_sent + self.bytes_recv
    
    def total_packets(self) -> int:
        """Total packets transferred."""
        return self.packets_sent + self.packets_recv


@dataclass
class FlowStat:
    """Represents a single network flow (5-tuple)."""
    protocol: Protocol
    local_ip: str
    local_port: int
    remote_ip: str
    remote_port: int
    bytes_up: int = 0  # Bytes from local to remote
    bytes_down: int = 0  # Bytes from remote to local
    packets_up: int = 0
    packets_down: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    process_name: Optional[str] = None  # Linux eBPF: optional per-process attribution
    process_pid: Optional[int] = None
    
    def total_bytes(self) -> int:
        """Total bytes transferred in this flow."""
        return self.bytes_up + self.bytes_down
    
    def __hash__(self):
        """Make FlowStat hashable for use in sets/dicts (by 5-tuple)."""
        return hash((self.protocol, self.local_ip, self.local_port, 
                     self.remote_ip, self.remote_port))
    
    def __eq__(self, other):
        """Equality based on 5-tuple."""
        if not isinstance(other, FlowStat):
            return False
        return (self.protocol == other.protocol and
                self.local_ip == other.local_ip and
                self.local_port == other.local_port and
                self.remote_ip == other.remote_ip and
                self.remote_port == other.remote_port)


@dataclass
class HostStat:
    """Aggregated statistics for a remote host."""
    ip: str
    hostname: Optional[str] = None
    total_bytes_up: int = 0
    total_bytes_down: int = 0
    packets_up: int = 0
    packets_down: int = 0
    last_seen: datetime = field(default_factory=datetime.now)
    flow_count: int = 0
    
    def total_bytes(self) -> int:
        """Total bytes transferred with this host."""
        return self.total_bytes_up + self.total_bytes_down


@dataclass
class AlertRule:
    """Represents an alert rule."""
    name: str
    metric: str  # e.g., "upload_rate_mbps"
    operator: str  # ">", "<", "==", etc.
    threshold: float
    duration_seconds: int = 10  # Alert if threshold exceeded for this duration
    enabled: bool = True
    interface_filter: Optional[str] = None  # None = all interfaces


@dataclass
class AppConfig:
    """Application configuration."""
    sampling_interval_ms: int = 1000  # 1 second
    retention_days: int = 30
    deep_capture_enabled: bool = False
    interface_selection: List[str] = field(default_factory=list)  # Empty = all
    privacy_no_hostname: bool = False
    privacy_limit_retention: bool = True
    alert_rules: List[AlertRule] = field(default_factory=list)
    chart_history_seconds: int = 300  # 5 minutes of history in chart
