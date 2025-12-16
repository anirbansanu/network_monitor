# core/connection_tracker.py
"""
Track per-connection upload/download bytes.
Uses socket-level inspection and interface-level tracking.
"""

import psutil
from datetime import datetime
from typing import Dict, Tuple
from collections import defaultdict

from models.data_models import FlowStat, Protocol


class ConnectionTracker:
    """
    Tracks upload/download bytes for active connections.
    Estimates bytes based on interface deltas and connection counts.
    """
    
    def __init__(self):
        # Store previous interface counters for delta calculation
        self.prev_counters: Dict[str, Tuple[int, int]] = {}  # iface -> (sent, recv)
        
        # Store bytes per connection
        self.connection_bytes: Dict[Tuple, Tuple[int, int]] = {}  # (proto, lip, lp, rip, rp) -> (up, down)
    
    def update_connection_stats(self) -> Dict[Tuple, Tuple[int, int]]:
        """
        Update connection statistics by examining active connections
        and estimating bytes based on random sampling.
        
        Returns:
            Dictionary mapping 5-tuple to (bytes_up, bytes_down)
        """
        # Get current interface stats
        try:
            counters = psutil.net_io_counters(pernic=True)
        except Exception as e:
            print(f"Error getting interface counters: {e}")
            return {}
        
        # Calculate deltas and distribute among connections
        active_connections = self._get_active_connections_5tuple()
        
        if not active_connections:
            return {}
        
        # Simple heuristic: distribute bytes proportionally
        # In reality, would need packet capture for accurate per-flow bytes
        total_delta_up = 0
        total_delta_down = 0
        
        for iface_name, counter in counters.items():
            if iface_name in self.prev_counters:
                prev_sent, prev_recv = self.prev_counters[iface_name]
                total_delta_up += max(0, counter.bytes_sent - prev_sent)
                total_delta_down += max(0, counter.bytes_recv - prev_recv)
            
            self.prev_counters[iface_name] = (counter.bytes_sent, counter.bytes_recv)
        
        # Distribute deltas proportionally among connections
        if total_delta_up > 0 or total_delta_down > 0:
            conn_count = len(active_connections)
            if conn_count > 0:
                bytes_per_conn_up = total_delta_up // conn_count
                bytes_per_conn_down = total_delta_down // conn_count
                
                for key in active_connections:
                    if key not in self.connection_bytes:
                        self.connection_bytes[key] = (0, 0)
                    
                    prev_up, prev_down = self.connection_bytes[key]
                    self.connection_bytes[key] = (
                        prev_up + bytes_per_conn_up,
                        prev_down + bytes_per_conn_down
                    )
        
        return self.connection_bytes
    
    def _get_active_connections_5tuple(self) -> set:
        """Get set of active 5-tuples."""
        result = set()
        try:
            connections = psutil.net_connections(kind='inet')
            for conn in connections:
                if conn.laddr and conn.raddr and conn.status == 'ESTABLISHED':
                    key = (
                        'TCP' if conn.type == 1 else 'UDP',
                        conn.laddr.ip,
                        conn.laddr.port,
                        conn.raddr.ip,
                        conn.raddr.port
                    )
                    result.add(key)
        except Exception as e:
            print(f"Error getting connections: {e}")
        
        return result
    
    def get_bytes_for_connection(self, proto: str, local_ip: str, local_port: int,
                                  remote_ip: str, remote_port: int) -> Tuple[int, int]:
        """Get bytes_up and bytes_down for a connection."""
        key = (proto, local_ip, local_port, remote_ip, remote_port)
        return self.connection_bytes.get(key, (0, 0))
