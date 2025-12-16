# core/packet_capture.py
"""
Packet capture abstraction for Windows (Npcap) and Linux (eBPF stub).
"""

import sys
from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from datetime import datetime

from models.data_models import FlowStat, Protocol


class PacketCaptureEngine(ABC):
    """Abstract base for packet capture implementations."""
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if capture engine is available (permissions, dependencies)."""
        pass
    
    @abstractmethod
    def start(self, interfaces: Optional[List[str]] = None):
        """Start capturing packets."""
        pass
    
    @abstractmethod
    def stop(self):
        """Stop capturing packets."""
        pass
    
    @abstractmethod
    def get_flows(self) -> List[FlowStat]:
        """Get captured flows since last call."""
        pass


class NpcapCaptureEngine(PacketCaptureEngine):
    """
    Windows Npcap-based packet capture.
    
    TODO: Full implementation requires:
    - Import pypcap or scapy with Npcap backend
    - Packet parsing (IPv4/IPv6, TCP/UDP)
    - 5-tuple aggregation in-memory
    - Periodic flushing of flow summaries
    """
    
    def __init__(self):
        self.is_running = False
        self._npcap_available = False
        self._detect_npcap()
    
    def _detect_npcap(self):
        """Detect if Npcap is installed on Windows."""
        if sys.platform != "win32":
            return
        
        try:
            # Attempt to import pcapy or scapy
            # This is a detection mechanism; actual import depends on environment
            # For now, we assume Npcap detection via registry or dll check
            import winreg
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Nmap\Npcap"
                )
                winreg.CloseKey(key)
                self._npcap_available = True
            except OSError:
                self._npcap_available = False
        except Exception as e:
            print(f"Npcap detection failed: {e}")
            self._npcap_available = False
    
    def is_available(self) -> bool:
        """Check if Npcap is available."""
        return self._npcap_available
    
    def start(self, interfaces: Optional[List[str]] = None):
        """
        Start capturing packets from interfaces.
        
        TODO: Implement packet capture loop using pcapy/scapy.
        """
        if not self.is_available():
            raise RuntimeError("Npcap not available")
        
        self.is_running = True
        print(f"Npcap capture started on interfaces: {interfaces}")
    
    def stop(self):
        """Stop packet capture."""
        self.is_running = False
        print("Npcap capture stopped")
    
    def get_flows(self) -> List[FlowStat]:
        """
        Get flows from captured packets.
        
        TODO: Parse pcap packets, extract 5-tuples, build FlowStat.
        For now, returns empty list (stub).
        """
        return []


class EbpfCaptureEngine(PacketCaptureEngine):
    """
    Linux eBPF-based packet capture for per-process attribution.
    
    TODO: Full implementation requires:
    - bcc (BPF Compiler Collection) or libbpf Python bindings
    - eBPF programs to hook into kernel network stack
    - Per-process mapping via task_struct
    - User-space aggregator to collect kernel-side data
    
    Current status: Stub with interface definition.
    """
    
    def __init__(self):
        self.is_running = False
        self._bcc_available = self._check_bcc()
    
    def _check_bcc(self) -> bool:
        """Check if BCC/eBPF tools are available on Linux."""
        if sys.platform != "linux":
            return False
        
        try:
            # Try to import bcc; if unavailable, stub returns False
            import bcc
            return True
        except ImportError:
            return False
    
    def is_available(self) -> bool:
        """Check if eBPF capture is available."""
        # For now, require root/cap_sys_resource
        import os
        return self._bcc_available and os.geteuid() == 0
    
    def start(self, interfaces: Optional[List[str]] = None):
        """
        Start eBPF-based packet capture.
        
        TODO: Load and attach eBPF programs to kprobes/tracepoints.
        Example outline:
        
        from bcc import BPF
        
        program = '''
        struct flow_key {
            u32 sip, dip;
            u16 sport, dport;
            u8 proto;
        };
        
        BPF_HASH(flows, struct flow_key, u64);  // Track bytes
        
        int trace_send(struct pt_regs *ctx, ...) {
            struct flow_key key = {...};
            flows.increment(key, packet_len);
            return 0;
        }
        '''
        
        bpf = BPF(text=program)
        bpf.attach_kprobe(event="tcp_v4_send_skb", fn_name="trace_send")
        ...
        """
        if not self._check_bcc():
            print("WARNING: bcc not installed. eBPF capture unavailable.")
            print("Install with: sudo apt install python3-bcc")
            return
        
        self.is_running = True
        print("eBPF capture started")
    
    def stop(self):
        """Stop eBPF capture."""
        self.is_running = False
        print("eBPF capture stopped")
    
    def get_flows(self) -> List[FlowStat]:
        """
        Fetch flows with per-process attribution from eBPF kernel data.
        
        TODO: Read from perf buffers or BPF maps, deserialize flow data.
        For now, returns empty list (stub).
        """
        return []


def get_capture_engine() -> PacketCaptureEngine:
    """
    Factory function to get the appropriate capture engine for the platform.
    """
    if sys.platform == "win32":
        return NpcapCaptureEngine()
    elif sys.platform == "linux":
        return EbpfCaptureEngine()
    else:
        raise NotImplementedError(f"Unsupported platform: {sys.platform}")
