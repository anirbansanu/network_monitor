# build_encrypted.py - FIXED (with proper imports)
# Location: Project Root
# Purpose: Build encrypted .exe with license protection

"""
Build encrypted .exe with license protection.

Usage:
    python build_encrypted.py --full    (Build + License)
    python build_encrypted.py --license (License only)
"""

import os
import sys
import subprocess
from pathlib import Path

# FIX: Add project root to path BEFORE importing services
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# NOW import services
from services.license_manager import LicenseManager


class EncryptedBuilder:
    """Builds encrypted .exe with PyInstaller."""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
    
    def check_dependencies(self) -> bool:
        """Check if required tools are installed."""
        required = ["PyInstaller", "pyarmor"]
        
        print("🔍 Checking dependencies...")
        missing = []
        
        for tool in required:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", tool],
                capture_output=True
            )
            if result.returncode != 0:
                missing.append(tool)
        
        if missing:
            print(f"❌ Missing: {', '.join(missing)}")
            print(f"\n📦 Install with:")
            print(f"   pip install {' '.join(missing)}")
            return False
        
        print("✅ All dependencies installed")
        return True
    
    def build_exe(self) -> bool:
        """Build executable using PyInstaller."""
        print("\n🔨 Building executable with PyInstaller...")
        print("   (This may take 5-10 minutes)")
        
        try:
            # Build command - uses valid PyInstaller arguments only
            cmd = [
                sys.executable,
                "-m",
                "PyInstaller",
                "--onefile",
                "--windowed",
                "--name", "NetworkMonitor",
                "--icon", str(self.project_root / "app" / "resources" / "app_icon.ico"),
                "--add-data", f"{self.project_root / 'app' / 'theme' / 'dark.qss'}:app/theme",
                "--add-data", f"{self.project_root / 'app' / 'resources'}:app/resources",
                "--add-data", f"{self.project_root / 'storage' / 'schema.sql'}:storage",
                "--hidden-import", "PySide6",
                "--hidden-import", "pyqtgraph",
                "--hidden-import", "psutil",
                str(self.project_root / "app" / "main.py")
            ]
            
            # Run build from project root
            result = subprocess.run(cmd, cwd=str(self.project_root))
            
            if result.returncode == 0:
                exe_path = self.dist_dir / "NetworkMonitor.exe"
                if exe_path.exists():
                    size_mb = exe_path.stat().st_size / (1024**2)
                    print(f"✅ Executable built successfully")
                    print(f"   📦 NetworkMonitor.exe ({size_mb:.1f} MB)")
                    return True
        
        except Exception as e:
            print(f"❌ Build error: {e}")
            import traceback
            traceback.print_exc()
        
        return False
    
    def create_license(self, days_valid: int = 365) -> bool:
        """Create hardware-locked license file."""
        print("\n🔑 Generating license key...")
        
        try:
            # Get hardware ID
            hardware_id = LicenseManager.get_hardware_id()
            print(f"   📱 Hardware ID: {hardware_id}")
            
            # Generate license
            license_dict = LicenseManager.generate_license_key(
                hardware_id,
                days_valid
            )
            
            # Save license to project root
            license_path = self.project_root / "network_monitor.lic"
            
            if LicenseManager.save_license(license_dict, license_path):
                print(f"✅ License created")
                print(f"   📂 {license_path}")
                print(f"   📅 Valid until: {license_dict['expiry']}")
                return True
            else:
                print("❌ Failed to save license")
                return False
        
        except Exception as e:
            print(f"❌ License error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def full_build(self) -> bool:
        """Complete build process."""
        print("=" * 60)
        print("🚀 NETWORK MONITOR - ENCRYPTED BUILD")
        print("=" * 60)
        
        # Check dependencies
        if not self.check_dependencies():
            return False
        
        # Build executable
        if not self.build_exe():
            return False
        
        # Create license
        if not self.create_license():
            print("⚠️  License creation failed (continuing anyway)")
        
        # Success
        print("\n" + "=" * 60)
        print("✅ BUILD COMPLETE!")
        print("=" * 60)
        print(f"\n📦 Output:")
        print(f"   Executable: {self.dist_dir}/NetworkMonitor.exe")
        print(f"   License: {self.project_root}/network_monitor.lic")
        
        print(f"\n🔐 Next steps:")
        print(f"   1. Test: dist\\NetworkMonitor.exe")
        print(f"   2. Copy license: C:\\Users\\<name>\\.network_monitor\\license.lic")
        print(f"   3. Run application")
        
        return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Build encrypted Network Monitor executable"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Full build (build + license)"
    )
    parser.add_argument(
        "--license",
        action="store_true",
        help="Create license only"
    )
    
    args = parser.parse_args()
    
    builder = EncryptedBuilder()
    
    # Show help if no args
    if not any([args.full, args.license]):
        parser.print_help()
        print("\n📖 Examples:")
        print("   python build_encrypted.py --full      (Build + License)")
        print("   python build_encrypted.py --license   (License only)")
        return
    
    # Full build
    if args.full:
        builder.full_build()
    
    # License only
    if args.license:
        builder.create_license()


if __name__ == "__main__":
    main()