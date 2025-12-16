# services/permission_service.py
"""
Permission and capability checking service.
"""

import os
import sys
from typing import Tuple


class PermissionService:
    """
    Checks for permissions and dependencies required for deep packet capture.
    """
    
    @staticmethod
    def is_admin() -> bool:
        """Check if running with admin/root privileges."""
        if sys.platform == "win32":
            try:
                import ctypes
                return ctypes.windll.shell.IsUserAnAdmin() != 0
            except Exception:
                return False
        else:  # Linux, macOS
            return os.geteuid() == 0
    
    @staticmethod
    def check_npcap() -> Tuple[bool, str]:
        """
        Check if Npcap is installed on Windows.
        
        Returns:
            (is_available, message)
        """
        if sys.platform != "win32":
            return False, "Npcap is Windows-only"
        
        try:
            import winreg
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Nmap\Npcap"
                )
                winreg.CloseKey(key)
                return True, "Npcap is installed"
            except OSError:
                return False, "Npcap not found in registry"
        except Exception as e:
            return False, f"Npcap check failed: {e}"
    
    @staticmethod
    def check_ebpf() -> Tuple[bool, str]:
        """
        Check if eBPF tools are available on Linux.
        
        Returns:
            (is_available, message)
        """
        if sys.platform != "linux":
            return False, "eBPF is Linux-only"
        
        if not PermissionService.is_admin():
            return False, "eBPF requires root/CAP_SYS_RESOURCE"
        
        try:
            import bcc
            return True, "BCC/eBPF is available"
        except ImportError:
            return False, "BCC not installed. Install with: sudo apt install python3-bcc"
    
    @staticmethod
    def get_capability_status() -> dict:
        """
        Get a comprehensive status of capture capabilities.
        
        Returns:
            Dictionary with status of each capability
        """
        is_admin = PermissionService.is_admin()
        npcap_available, npcap_msg = PermissionService.check_npcap()
        ebpf_available, ebpf_msg = PermissionService.check_ebpf()
        
        return {
            "is_admin": is_admin,
            "platform": sys.platform,
            "npcap_available": npcap_available,
            "npcap_message": npcap_msg,
            "ebpf_available": ebpf_available,
            "ebpf_message": ebpf_msg,
            "deep_capture_possible": (npcap_available and is_admin) or ebpf_available,
        }
