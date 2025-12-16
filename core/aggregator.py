# core/aggregator.py
"""
Aggregates low-level samples into UI-facing models.
Converts interface samples and flow data into HostStat, etc.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict

from models.data_models import InterfaceStat, FlowStat, HostStat, Protocol


class Aggregator:
    """
    Aggregates network data for UI consumption.
    """
    
    def __init__(self):
        self.flows: Dict[Tuple, FlowStat] = {}  # 5-tuple -> FlowStat
        self.hosts: Dict[str, HostStat] = {}  # IP -> HostStat
    
    def update_flow(self, flow: FlowStat):
        """
        Update or insert a flow.
        
        Args:
            flow: FlowStat to merge
        """
        key = (flow.protocol, flow.local_ip, flow.local_port,
               flow.remote_ip, flow.remote_port)
        
        if key in self.flows:
            existing = self.flows[key]
            existing.bytes_up += flow.bytes_up
            existing.bytes_down += flow.bytes_down
            existing.packets_up += flow.packets_up
            existing.packets_down += flow.packets_down
            existing.last_seen = datetime.now()
        else:
            self.flows[key] = flow
        
        # Update host aggregates
        self._update_host(flow.remote_ip, flow.bytes_up, flow.bytes_down,
                         flow.packets_up, flow.packets_down)
    
    def _update_host(self, ip: str, bytes_up: int, bytes_down: int,
                     packets_up: int, packets_down: int):
        """Update HostStat for a given IP."""
        if ip not in self.hosts:
            self.hosts[ip] = HostStat(ip=ip)
        
        host = self.hosts[ip]
        host.total_bytes_up += bytes_up
        host.total_bytes_down += bytes_down
        host.packets_up += packets_up
        host.packets_down += packets_down
        host.last_seen = datetime.now()
        host.flow_count = len([f for f in self.flows.values() 
                              if f.remote_ip == ip])
    
    def get_active_flows(self, timeout_sec: int = 30) -> List[FlowStat]:
        """
        Get flows that have been seen in the last timeout_sec seconds.
        
        Args:
            timeout_sec: Consider a flow active if last_seen within this duration
        
        Returns:
            List of active FlowStat objects
        """
        cutoff = datetime.now() - timedelta(seconds=timeout_sec)
        return [f for f in self.flows.values() if f.last_seen > cutoff]
    
    def get_top_hosts(self, count: int = 5, by: str = "total_bytes",
                      timeout_sec: int = 30) -> List[HostStat]:
        """
        Get top hosts by bytes transferred (active in last timeout_sec).
        
        Args:
            count: Number of top hosts to return
            by: "total_bytes" or "upload" or "download"
            timeout_sec: Only include hosts active within this duration
        
        Returns:
            List of top HostStat objects
        """
        cutoff = datetime.now() - timedelta(seconds=timeout_sec)
        active_hosts = [h for h in self.hosts.values() if h.last_seen > cutoff]
        
        if by == "total_bytes":
            sorted_hosts = sorted(active_hosts, 
                                 key=lambda h: h.total_bytes(), 
                                 reverse=True)
        elif by == "upload":
            sorted_hosts = sorted(active_hosts, 
                                 key=lambda h: h.total_bytes_up, 
                                 reverse=True)
        elif by == "download":
            sorted_hosts = sorted(active_hosts, 
                                 key=lambda h: h.total_bytes_down, 
                                 reverse=True)
        else:
            sorted_hosts = active_hosts
        
        return sorted_hosts[:count]
    
    def get_flow_by_remote(self, remote_ip: str) -> List[FlowStat]:
        """Get all flows to/from a specific remote IP."""
        return [f for f in self.flows.values() if f.remote_ip == remote_ip]
    
    def cleanup_old_flows(self, timeout_sec: int = 300):
        """
        Remove flows that haven't been seen in timeout_sec seconds.
        
        Args:
            timeout_sec: Remove flows inactive for this duration
        """
        cutoff = datetime.now() - timedelta(seconds=timeout_sec)
        to_remove = [k for k, f in self.flows.items() if f.last_seen < cutoff]
        
        for key in to_remove:
            del self.flows[key]
    
    def cleanup_old_hosts(self, timeout_sec: int = 300):
        """Remove hosts that haven't been seen in timeout_sec seconds."""
        cutoff = datetime.now() - timedelta(seconds=timeout_sec)
        to_remove = [ip for ip, h in self.hosts.items() if h.last_seen < cutoff]
        
        for ip in to_remove:
            del self.hosts[ip]
    
    def clear(self):
        """Clear all aggregated data."""
        self.flows.clear()
        self.hosts.clear()
