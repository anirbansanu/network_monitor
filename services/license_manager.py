# services/license_manager.py
"""
License management and hardware binding.
Prevents unauthorized copying and redistribution.
"""

import hashlib
import uuid
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Tuple, Optional


class LicenseManager:
    """
    Manages application licensing and hardware binding.
    """
    
    @staticmethod
    def get_hardware_id() -> str:
        """
        Get unique hardware identifier (MAC address).
        
        Returns:
            Hexadecimal string of MAC address
        """
        try:
            mac = uuid.getnode()
            return format(mac, '012x')
        except Exception as e:
            print(f"Error getting hardware ID: {e}")
            return "00000000000"
    
    @staticmethod
    def generate_license_key(hardware_id: str, expiry_days: int = 365) -> dict:
        """
        Generate a license key tied to hardware.
        
        Args:
            hardware_id: MAC address or hardware identifier
            expiry_days: Days until license expires
        
        Returns:
            Dictionary with license info
        """
        issued_date = datetime.now()
        expiry_date = issued_date + timedelta(days=expiry_days)
        
        # Create signature
        data = f"{hardware_id}{issued_date.isoformat()}{expiry_date.isoformat()}"
        signature = hashlib.sha256(data.encode()).hexdigest()[:16]
        
        return {
            "hardware_id": hardware_id,
            "issued": issued_date.isoformat(),
            "expiry": expiry_date.isoformat(),
            "signature": signature,
            "version": "1.0"
        }
    
    @staticmethod
    def validate_license(license_dict: dict, hardware_id: str) -> Tuple[bool, str]:
        """
        Validate a license key.
        
        Args:
            license_dict: License dictionary
            hardware_id: Current hardware ID
        
        Returns:
            (is_valid, message)
        """
        # Check if hardware matches
        if license_dict.get("hardware_id") != hardware_id:
            return False, "License not valid for this machine"
        
        # Check expiry
        expiry_str = license_dict.get("expiry")
        if expiry_str:
            expiry = datetime.fromisoformat(expiry_str)
            if datetime.now() > expiry:
                days_expired = (datetime.now() - expiry).days
                return False, f"License expired {days_expired} days ago"
        
        # Verify signature
        issued = license_dict.get("issued")
        data = f"{hardware_id}{issued}{expiry_str}"
        expected_sig = hashlib.sha256(data.encode()).hexdigest()[:16]
        
        if license_dict.get("signature") != expected_sig:
            return False, "License signature invalid (may be tampered)"
        
        return True, "License valid"
    
    @staticmethod
    def save_license(license_dict: dict, license_path: Path = None) -> bool:
        """
        Save license to file.
        
        Args:
            license_dict: License dictionary
            license_path: Path to save license file
        
        Returns:
            True if successful
        """
        if license_path is None:
            license_path = Path.home() / ".network_monitor" / "license.lic"
        
        try:
            license_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Simple encryption: just hex encode the JSON
            license_json = json.dumps(license_dict)
            encrypted = license_json.encode().hex()
            
            with open(license_path, 'w') as f:
                f.write(encrypted)
            
            return True
        except Exception as e:
            print(f"Error saving license: {e}")
            return False
    
    @staticmethod
    def load_license(license_path: Path = None) -> Optional[dict]:
        """
        Load license from file.
        
        Args:
            license_path: Path to license file
        
        Returns:
            License dictionary or None
        """
        if license_path is None:
            license_path = Path.home() / ".network_monitor" / "license.lic"
        
        try:
            if not license_path.exists():
                return None
            
            with open(license_path, 'r') as f:
                encrypted = f.read()
            
            # Simple decryption: hex decode to JSON
            license_json = bytes.fromhex(encrypted).decode()
            license_dict = json.loads(license_json)
            
            return license_dict
        except Exception as e:
            print(f"Error loading license: {e}")
            return None


class ApplicationGuard:
    """
    Application protection and anti-debugging features.
    """
    
    @staticmethod
    def detect_debugger() -> bool:
        """
        Detect if application is being debugged.
        
        Returns:
            True if debugger detected
        """
        import sys
        
        # Check if running under debugger
        if hasattr(sys, 'gettrace'):
            if sys.gettrace() is not None:
                return True
        
        # Check for common debuggers
        try:
            import ctypes
            # Windows specific
            if sys.platform == "win32":
                kernel32 = ctypes.windll.kernel32
                is_debugged = kernel32.IsDebuggerPresent()
                return bool(is_debugged)
        except Exception:
            pass
        
        return False
    
    @staticmethod
    def detect_vm() -> bool:
        """
        Detect if running in virtual machine.
        
        Returns:
            True if VM detected
        """
        import platform
        
        # Check for common VM identifiers
        try:
            system = platform.system()
            release = platform.release()
            
            vm_indicators = [
                "vmware", "virtualbox", "hyperv", "kvm",
                "qemu", "parallels", "vbox", "xen"
            ]
            
            for indicator in vm_indicators:
                if indicator in platform.platform().lower():
                    return True
                if indicator in release.lower():
                    return True
        except Exception:
            pass
        
        return False
    
    @staticmethod
    def check_integrity() -> Tuple[bool, str]:
        """
        Check application file integrity.
        
        Returns:
            (is_intact, message)
        """
        try:
            import hashlib
            from pathlib import Path
            
            exe_path = Path(sys.executable)
            
            if not exe_path.exists():
                return False, "Executable not found"
            
            # In production, compare against known good hash
            # For now, just check file is readable
            file_size = exe_path.stat().st_size
            
            if file_size < 1000000:  # Should be > 1MB
                return False, "Executable appears corrupted"
            
            return True, "Integrity check passed"
        except Exception as e:
            return False, f"Integrity check failed: {e}"
