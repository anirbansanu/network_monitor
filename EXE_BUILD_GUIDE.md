# Network Monitor - Complete .EXE Build Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Simple Build (No Encryption)](#simple-build-no-encryption)
3. [Encrypted Build (Recommended)](#encrypted-build-recommended)
4. [Troubleshooting](#troubleshooting)
5. [Distribution](#distribution)

---

## Prerequisites

### System Requirements
- **OS**: Windows 10 or later
- **Python**: 3.11+ (64-bit recommended)
- **RAM**: 4GB minimum
- **Disk Space**: 2GB for build process

### Step 1: Verify Python Installation

Open Command Prompt and run:

```bash
python --version
```

Expected output: `Python 3.11.x` or higher

If not installed, download from: https://www.python.org/downloads/

**Important**: Check "Add Python to PATH" during installation

### Step 2: Verify Project Structure

Your project should look like:

```
network_monitor/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── main_window.py
│   ├── resources.py
│   ├── resources/
│   │   └── app_icon.png
│   ├── screens/
│   ├── widgets/
│   └── theme/
│       └── dark.qss
├── core/
├── models/
├── storage/
├── services/
├── tests/
├── requirements.txt
├── requirements_build.txt
├── pyinstaller_build.spec
├── build_encrypted.py
├── run.py
└── README.md
```

---

## Simple Build (No Encryption)

For quick testing without security features.

### Step 1: Navigate to Project Directory

```bash
cd C:\path\to\network_monitor
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` at the start of command line.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
pip install PyInstaller
```

Wait for installation to complete (~2-3 minutes).

### Step 4: Build Executable

```bash
pyinstaller pyinstaller_build.spec
```

**Output**:
- Build process takes 2-5 minutes
- Creates `dist/NetworkMonitor/` folder
- Main executable: `dist/NetworkMonitor/NetworkMonitor.exe`

### Step 5: Test the Executable

```bash
dist/NetworkMonitor/NetworkMonitor.exe
```

The application should launch without needing Python installed!

### Troubleshooting Simple Build

**Error: "module not found"**
```bash
# Make sure all requirements installed
pip install -r requirements.txt -v
```

**Error: "PyInstaller not found"**
```bash
pip install PyInstaller --upgrade
```

**Missing icon or theme**
Check that these files exist:
```
app/resources/app_icon.png
app/theme/dark.qss
```

---

## Encrypted Build (Recommended)

For production with code protection and licensing.

### Step 1: Install Additional Build Tools

```bash
pip install -r requirements_build.txt
pip install pyarmor
```

### Step 2: Download and Install PyArmor

PyArmor requires separate installation:

**Option A: Via Python Package**
```bash
pip install pyarmor
```

**Option B: Manual Installation**
1. Visit: https://pyarmor.readthedocs.io/
2. Download latest version
3. Extract and run installer

**Verify Installation**:
```bash
pyarmor --version
```

Should show version number (e.g., `8.x.x`)

### Step 3: Prepare for Encrypted Build

Verify these files exist:
```
app/resources/app_icon.png
build_encrypted.py
pyinstaller_build.spec
requirements_build.txt
```

### Step 4: Run Full Encrypted Build

**Activate virtual environment** (if not already):
```bash
venv\Scripts\activate
```

**Run build**:
```bash
python build_encrypted.py --full
```

**What happens**:
1. Checks all dependencies (2-3 seconds)
2. Obfuscates code (1-2 minutes)
3. Encrypts executable (3-5 minutes)
4. Generates license file (1 second)
5. Creates final .exe (2-3 minutes)

**Total time**: 5-12 minutes

**Output**:
```
dist/NetworkMonitor/NetworkMonitor.exe
network_monitor.lic (license file)
```

### Step 5: Test Encrypted Executable

**Test 1: Run with license**
```bash
# Copy license to home folder
mkdir %USERPROFILE%\.network_monitor
copy network_monitor.lic %USERPROFILE%\.network_monitor\

# Run executable
dist/NetworkMonitor/NetworkMonitor.exe
```

**Test 2: Run without license**
```bash
# Delete license
del %USERPROFILE%\.network_monitor\license.lic

# Try to run (should fail)
dist/NetworkMonitor/NetworkMonitor.exe
```

---

## Step-by-Step Build Process

### For Simple Build:

```
Start
  ↓
[1] Install Python 3.11+
  ↓
[2] Navigate to project folder
  ↓
[3] Create virtual environment: python -m venv venv
  ↓
[4] Activate: venv\Scripts\activate
  ↓
[5] Install deps: pip install -r requirements.txt
  ↓
[6] Install PyInstaller: pip install PyInstaller
  ↓
[7] Build: pyinstaller pyinstaller_build.spec
  ↓
[8] Test: dist/NetworkMonitor/NetworkMonitor.exe
  ↓
End ✓
```

### For Encrypted Build:

```
Start
  ↓
[1-6] Same as above (steps 1-6)
  ↓
[7] Install PyArmor: pip install pyarmor
  ↓
[8] Install build tools: pip install -r requirements_build.txt
  ↓
[9] Full build: python build_encrypted.py --full
  ↓
[10] Copy license: mkdir .network_monitor
     copy network_monitor.lic %USERPROFILE%\.network_monitor\
  ↓
[11] Test: dist/NetworkMonitor/NetworkMonitor.exe
  ↓
End ✓
```

---

## Build Options

### Option 1: Simple Unencrypted (Fast)

```bash
pyinstaller pyinstaller_build.spec
```

- **Time**: 3-5 minutes
- **Size**: 120-150 MB
- **Security**: Low (code can be extracted)
- **Use**: Testing, internal distribution

### Option 2: Encrypted Only

```bash
python build_encrypted.py --build
```

- **Time**: 5-7 minutes
- **Size**: 120-150 MB
- **Security**: High (code encrypted)
- **Use**: Production, basic protection

### Option 3: Obfuscated + Encrypted (Most Secure)

```bash
python build_encrypted.py --full
```

- **Time**: 10-15 minutes
- **Size**: 120-150 MB
- **Security**: Very High (obfuscated + encrypted + license)
- **Use**: Commercial, serious protection

### Option 4: With UPX Compression (Smaller)

Requires UPX installed: https://upx.github.io/

```bash
# UPX will be used automatically if available
python build_encrypted.py --full
```

- **Result Size**: 40-60 MB (50% smaller)
- **Trade-off**: Slightly slower startup (~1-2 seconds)

---

## Understanding the Output

### Simple Build Output

```
dist/NetworkMonitor/
├── NetworkMonitor.exe        (Main application)
├── _internal/                (Python runtime + dependencies)
│   ├── python3.11.dll
│   ├── PySide6/
│   ├── pyqtgraph/
│   └── ... (other DLLs)
├── app/                       (Application files)
│   ├── theme/
│   │   └── dark.qss
│   └── resources/
│       └── app_icon.png
└── storage/
    └── schema.sql
```

### Encrypted Build Output

```
dist/NetworkMonitor/
├── NetworkMonitor.exe        (Encrypted executable)
├── _internal/                (Encrypted Python runtime)
└── pyarmor_runtime/          (PyArmor runtime library)

network_monitor.lic           (License file - user-specific)
```

---

## Distribution to Users

### For Simple Build:

1. **Create distribution folder**:
   ```bash
   mkdir NetworkMonitor_dist
   ```

2. **Copy the entire dist/NetworkMonitor folder**:
   ```bash
   xcopy dist\NetworkMonitor NetworkMonitor_dist\NetworkMonitor /E /I
   ```

3. **Create shortcut** (optional):
   - Right-click `NetworkMonitor.exe`
   - "Create shortcut"
   - Place on Desktop

4. **Send to users**: `NetworkMonitor_dist\` folder

**User instructions**:
```
1. Extract the folder
2. Double-click NetworkMonitor.exe
3. Application starts
```

### For Encrypted Build:

1. **Build for user's machine**:
   ```bash
   python build_encrypted.py --license
   ```
   (Generates `network_monitor.lic` for current hardware)

2. **Package**:
   - `dist/NetworkMonitor/NetworkMonitor.exe`
   - `network_monitor.lic`

3. **Send to user with instructions**:

**User Instructions**:
```
1. Extract NetworkMonitor.exe to desired location
2. Create folder: C:\Users\YourName\.network_monitor
3. Copy network_monitor.lic to that folder
4. Run NetworkMonitor.exe

If license errors:
- Verify license file is in: C:\Users\YourName\.network_monitor\license.lic
- Check license is valid (hasn't expired)
```

---

## Common Issues & Solutions

### Issue 1: "No module named 'PySide6'"

**Solution**:
```bash
pip install PySide6 --upgrade
pip install -r requirements.txt
```

### Issue 2: "PyInstaller not found"

**Solution**:
```bash
pip install PyInstaller --upgrade
python -m pip install PyInstaller
```

### Issue 3: Build takes too long or hangs

**Solution**:
- Close other programs (especially antivirus)
- Use faster disk (SSD preferred)
- Try: `pyinstaller --onefile pyinstaller_build.spec`

### Issue 4: "icon file not found"

**Solution**:
Ensure `app/resources/app_icon.png` exists:
```bash
dir app\resources\
```

If missing, regenerate or use placeholder.

### Issue 5: Executable won't start

**Possible causes**:
1. Missing `dark.qss` theme file
2. Missing `schema.sql` database schema
3. Missing app icon resource
4. Corrupted .exe from antivirus

**Solution**:
```bash
# Verify all files copied
dir dist\NetworkMonitor\

# Check for quarantined files in antivirus
# Rebuild if needed
pyinstaller pyinstaller_build.spec --clean
```

### Issue 6: Application crashes immediately

**Debug steps**:
1. Run from command line to see error:
   ```bash
   dist\NetworkMonitor\NetworkMonitor.exe
   ```

2. Check logs (if any created)

3. Rebuild with console to see errors:
   ```bash
   pyinstaller pyinstaller_build.spec --console
   ```

### Issue 7: License not found error (Encrypted build)

**Causes**:
- License file not in correct location
- License expired
- License for different machine

**Solution**:
```bash
# Check hardware ID
python -c "from services.license_manager import LicenseManager; print(LicenseManager.get_hardware_id())"

# Regenerate license for current machine
python build_encrypted.py --license

# Copy to correct location
mkdir %USERPROFILE%\.network_monitor
copy network_monitor.lic %USERPROFILE%\.network_monitor\
```

---

## Optimization Tips

### Reduce File Size

**Enable UPX compression** (if installed):
```bash
# UPX must be in PATH
# Download from: https://upx.github.io/

# Then build normally
python build_encrypted.py --full
```

Result: 120 MB → 40-60 MB

### Speed Up Build

```bash
# Skip antivirus scanning during build
# (Temporarily disable Windows Defender, if safe)

# Use SSD for faster I/O

# Close unnecessary programs
```

### Faster Startup

```bash
# Use single-file executable
pyinstaller --onefile pyinstaller_build.spec

# Trade-off: Slower startup, larger single file
```

---

## Advanced: Customization

### Change Encryption Key

Edit `build_encrypted.py`:
```python
# Line in full_build() method
"--encrypt-key", "YourCustomKeyHere",
```

### Change License Validity

Edit `build_encrypted.py`:
```python
def create_license(self, days_valid: int = 365) -> bool:
    # Change 365 to desired number of days
```

### Add Windows Signing

For production certificates:
```bash
signtool sign /f cert.pfx /p password /t http://timestamp.comodoca.com/rfc3161 dist/NetworkMonitor/NetworkMonitor.exe
```

---

## Verification Checklist

After building, verify:

- [ ] `.exe` file exists in `dist/NetworkMonitor/`
- [ ] `.exe` is larger than 100MB (includes Python runtime)
- [ ] Application launches without errors
- [ ] All UI screens work (Dashboard, Interfaces, Connections, Settings)
- [ ] Network monitoring shows connections
- [ ] Dark theme loads correctly
- [ ] Settings can be saved

For encrypted build, also:
- [ ] License file generated (`network_monitor.lic`)
- [ ] Application runs with license present
- [ ] Application refuses to run without license (if configured)
- [ ] Code cannot be extracted (use: `strings NetworkMonitor.exe | grep "def main"` - should show nothing)

---

## Performance Profile

### Build Time (Full Encrypted)

```
Stage 1: Obfuscation      1-2 minutes
Stage 2: Build            3-5 minutes  
Stage 3: License Gen      1 second
Total:                    5-10 minutes
```

### Startup Time

- **Simple build**: 2-3 seconds
- **Encrypted**: 2-4 seconds (with license check)
- **Subsequent runs**: Same (no caching)

### Runtime Performance

- **No noticeable difference** from running Python directly
- Obfuscation adds <5% overhead
- License check adds <500ms

---

## Support & Resources

### Official Documentation

- **PyInstaller**: https://pyinstaller.org/
- **PyArmor**: https://pyarmor.readthedocs.io/
- **PySide6**: https://doc.qt.io/qtforpython/

### Tools & Downloads

- **Python**: https://www.python.org/downloads/
- **PyArmor**: https://pyarmor.readthedocs.io/
- **UPX**: https://upx.github.io/
- **Code Signing Cert**: https://comodosslstore.com/

### Community Help

- Stack Overflow: `pyinstaller` tag
- Python Discord: #dev channel
- GitHub Issues: Report bugs

---

## Summary

### Quick Reference

**Simple Build** (Testing):
```bash
pyinstaller pyinstaller_build.spec
```

**Encrypted Build** (Production):
```bash
python build_encrypted.py --full
```

**Test**:
```bash
dist/NetworkMonitor/NetworkMonitor.exe
```

**Distribute**:
```bash
# Copy dist/NetworkMonitor folder to users
# Copy network_monitor.lic (for encrypted)
```

---

## Congratulations! 🎉

You now have a professional `.exe` file ready for distribution!

**Next Steps**:
1. Test thoroughly on clean machines
2. Create user documentation
3. Set up license management system (if encrypted)
4. Distribute to users
5. Collect feedback

**Questions?** Refer to troubleshooting section or official documentation links above.

---

**Last Updated**: December 15, 2025  
**Version**: 1.0  
**Network Monitor**: Complete Build Guide
