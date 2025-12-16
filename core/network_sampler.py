# core/network_sampler.py
"""
Basic network sampler using psutil.
No admin required; provides interface-level counters and connection info.
"""

import psutil
from datetime import datetime
from typing import Dict, List

from models.data_models import InterfaceStat, FlowStat, Protocol
from core.rate_calculator import RateCalculator
from core.connection_tracker import ConnectionTracker


class NetworkSampler:
    """
    Samples interface-level network statistics using psutil.
    Also collects active connections (TCP/UDP) with byte tracking.
    No admin/root required.
    """
    
    def __init__(self):
        self.rate_calculator = RateCalculator()
        self.connection_tracker = ConnectionTracker()
    
    def sample(self) -> Dict[str, InterfaceStat]:
        """
        Sample current interface statistics.
        
        Returns:
            Dictionary mapping interface name to InterfaceStat
        """
        result = {}
        now = datetime.now()
        
        try:
            counters = psutil.net_io_counters(pernic=True)
        except Exception as e:
            print(f"Error sampling network counters: {e}")
            return result
        
        for iface_name, counter in counters.items():
            # Calculate rates
            rate_up, rate_down = self.rate_calculator.add_sample(
                iface_name, now,
                counter.bytes_sent,
                counter.bytes_recv
            )
            
            stat = InterfaceStat(
                name=iface_name,
                bytes_sent=counter.bytes_sent,
                bytes_recv=counter.bytes_recv,
                packets_sent=counter.packets_sent,
                packets_recv=counter.packets_recv,
                rate_up_mbps=rate_up,
                rate_down_mbps=rate_down,
                is_up=True,
                timestamp=now
            )
            result[iface_name] = stat
        
        return result
    
    def get_active_connections(self) -> List[FlowStat]:
        """
        Get active TCP/UDP connections using psutil with byte tracking.
        
        Returns:
            List of FlowStat objects representing active connections
        """
        flows = []
        now = datetime.now()
        
        # Update connection byte stats
        self.connection_tracker.update_connection_stats()
        
        try:
            # Get all network connections
            connections = psutil.net_connections(kind='inet')
            
            for conn in connections:
                # Skip if missing required fields
                if not conn.laddr or not conn.raddr:
                    continue
                
                # Only track established connections
                if conn.status != 'ESTABLISHED':
                    continue
                
                # Parse protocol
                if conn.type == 1:  # SOCK_STREAM = TCP
                    protocol = Protocol.TCP
                elif conn.type == 2:  # SOCK_DGRAM = UDP
                    protocol = Protocol.UDP
                else:
                    continue
                
                # Extract address info
                local_ip = conn.laddr.ip
                local_port = conn.laddr.port
                remote_ip = conn.raddr.ip
                remote_port = conn.raddr.port
                
                # Get bytes for this connection
                bytes_up, bytes_down = self.connection_tracker.get_bytes_for_connection(
                    protocol.value, local_ip, local_port, remote_ip, remote_port
                )
                
                # Get process info if available
                process_name = None
                process_pid = None
                try:
                    if conn.pid:
                        proc = psutil.Process(conn.pid)
                        process_name = proc.name()
                        process_pid = conn.pid
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                
                # Create flow stat
                flow = FlowStat(
                    protocol=protocol,
                    local_ip=local_ip,
                    local_port=local_port,
                    remote_ip=remote_ip,
                    remote_port=remote_port,
                    bytes_up=bytes_up,
                    bytes_down=bytes_down,
                    packets_up=0,
                    packets_down=0,
                    process_name=process_name,
                    process_pid=process_pid,
                    start_time=now,
                    last_seen=now
                )
                
                flows.append(flow)
        
        except Exception as e:
            print(f"Error getting connections: {e}")
        
        return flows
    
    def get_interface_names(self) -> list[str]:
        """Get list of available network interfaces."""
        try:
            stats = psutil.net_if_stats()
            return list(stats.keys())
        except Exception as e:
            print(f"Error getting interface names: {e}")
            return []
