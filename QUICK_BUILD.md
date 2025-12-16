# Network Monitor - Quick .EXE Build Guide

## ⚡ Super Fast (5 Minutes)

### Simple Build - Unencrypted

```bash
# 1. Navigate to project
cd C:\path\to\network_monitor

# 2. Create environment
python -m venv venv
venv\Scripts\activate

# 3. Install
pip install -r requirements.txt PyInstaller

# 4. Build
pyinstaller pyinstaller_build.spec

# 5. Run
dist\NetworkMonitor\NetworkMonitor.exe
```

**Time**: 5-8 minutes  
**Result**: `dist/NetworkMonitor/NetworkMonitor.exe`  
**Size**: 120-150 MB

---

## 🔒 Encrypted Build (Recommended - 15 Minutes)

### Production-Ready with License

```bash
# 1. Navigate to project
cd C:\path\to\network_monitor

# 2. Create environment
python -m venv venv
venv\Scripts\activate

# 3. Install all tools
pip install -r requirements.txt -r requirements_build.txt
pip install pyarmor

# 4. Build encrypted
python build_encrypted.py --full

# 5. Setup license
mkdir %USERPROFILE%\.network_monitor
copy network_monitor.lic %USERPROFILE%\.network_monitor\

# 6. Run
dist\NetworkMonitor\NetworkMonitor.exe
```

**Time**: 10-15 minutes  
**Result**: 
- `dist/NetworkMonitor/NetworkMonitor.exe` (encrypted)
- `network_monitor.lic` (license file)  
**Size**: 120-150 MB  
**Security**: Code obfuscated + encrypted + hardware-bound

---

## 🎯 What Gets Built

```
dist/NetworkMonitor/
├── NetworkMonitor.exe         ← Main app
├── _internal/                 ← Python runtime
└── app/, storage/ folders     ← Resources
```

**That's it!** One folder with everything needed.

---

## 📦 Send to Users

### Simple Version:
1. Copy `dist/NetworkMonitor/` folder
2. User extracts and runs `NetworkMonitor.exe`
3. Done ✓

### Encrypted Version:
1. Copy `dist/NetworkMonitor/` folder
2. Copy `network_monitor.lic` to user
3. User places `.lic` in `C:\Users\<name>\.network_monitor\`
4. User runs `NetworkMonitor.exe`
5. App validates license and starts

---

## ✅ Verification

After build:
```bash
# Check if .exe exists
dir dist\NetworkMonitor\

# Test it
dist\NetworkMonitor\NetworkMonitor.exe
```

**✓ Should see**: Application window opens immediately

---

## 🛠️ Troubleshooting

| Error | Fix |
|-------|-----|
| "No module named X" | `pip install -r requirements.txt` |
| "PyInstaller not found" | `pip install PyInstaller` |
| ".exe won't start" | Ensure `app/theme/dark.qss` exists |
| "License error" | Copy `.lic` to `C:\Users\<name>\.network_monitor\` |

---

## 📊 Comparison

| Method | Time | Size | Security | For |
|--------|------|------|----------|-----|
| Simple | 5 min | 130 MB | Low | Testing |
| Encrypted | 15 min | 130 MB | High | Production |
| With UPX | 15 min | 50 MB | High | Deployment |

---

## 🎓 Key Points

- ✅ No Python needed on user's machine
- ✅ Single .exe file (+ DLLs in _internal folder)
- ✅ Works offline after installed
- ✅ Can be packaged as ZIP or installer
- ✅ Encrypted version prevents code theft
- ✅ License binds to hardware MAC address

---

## 🚀 Summary

**For Testing**: 
```bash
pyinstaller pyinstaller_build.spec
```

**For Production**: 
```bash
python build_encrypted.py --full
```

**Test It**:
```bash
dist\NetworkMonitor\NetworkMonitor.exe
```

---

**That's all you need!** 🎉
