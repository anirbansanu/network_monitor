# core/rate_calculator.py
"""
Rate calculation utilities.
Computes upload/download rates from interface samples.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Tuple


@dataclass
class Sample:
    """A single sample point in time."""
    timestamp: datetime
    bytes_sent: int
    bytes_recv: int


class RateCalculator:
    """
    Calculates rates (Mbps) from successive interface samples.
    """
    
    def __init__(self):
        self.samples: Dict[str, list[Sample]] = {}  # interface_name -> [samples]
    
    def add_sample(self, interface_name: str, timestamp: datetime, 
                   bytes_sent: int, bytes_recv: int) -> Tuple[float, float]:
        """
        Add a sample and return (rate_up_mbps, rate_down_mbps).
        
        Args:
            interface_name: Name of the interface
            timestamp: Timestamp of the sample
            bytes_sent: Total bytes sent (cumulative)
            bytes_recv: Total bytes received (cumulative)
        
        Returns:
            (rate_up_mbps, rate_down_mbps) for this sample period
        """
        if interface_name not in self.samples:
            self.samples[interface_name] = []
        
        samples = self.samples[interface_name]
        
        # Keep only last 2 samples for rate calculation
        if len(samples) >= 2:
            samples.pop(0)
        
        samples.append(Sample(timestamp, bytes_sent, bytes_recv))
        
        # Need at least 2 samples to calculate rate
        if len(samples) < 2:
            return 0.0, 0.0
        
        prev_sample = samples[0]
        curr_sample = samples[1]
        
        # Calculate delta
        delta_sent = curr_sample.bytes_sent - prev_sample.bytes_sent
        delta_recv = curr_sample.bytes_recv - prev_sample.bytes_recv
        delta_time_sec = (curr_sample.timestamp - prev_sample.timestamp).total_seconds()
        
        if delta_time_sec <= 0:
            return 0.0, 0.0
        
        # Convert bytes/sec to Mbps
        rate_up_mbps = (delta_sent * 8) / (delta_time_sec * 1_000_000)
        rate_down_mbps = (delta_recv * 8) / (delta_time_sec * 1_000_000)
        
        return max(0.0, rate_up_mbps), max(0.0, rate_down_mbps)
    
    def clear(self, interface_name: str):
        """Clear samples for an interface."""
        if interface_name in self.samples:
            del self.samples[interface_name]
