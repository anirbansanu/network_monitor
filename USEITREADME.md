# Network Monitor - User Guide

This guide provides comprehensive instructions for installing, configuring, and using the Network Monitor application.

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Installation & Setup](#installation--setup)
4. [Running the Application](#running-the-application)
5. [Using the Application](#using-the-application)
6. [Building executables](#building-executables)
7. [Troubleshooting](#troubleshooting)

## 🚀 Project Overview

Network Monitor is a professional-grade desktop application for real-time network traffic analysis. It monitors bandwidth usage, tracks active connections, and provides detailed statistics per network interface.

**Key Features:**
*   **Real-Time Dashboard:** View up/down speeds, total data transfer, and top active remote hosts.
*   **Interface Monitoring:** Detailed stats for each network adapter (Wi-Fi, Ethernet, etc.).
*   **Connection Tracking:** See which apps are connecting to where (Process ID, remote IP, port, protocol).
*   **Historical Data:** Data is saved locally for historical analysis.
*   **Privacy Focused:** Options to anonymize hostnames and limit data retention.

## 🛠 Prerequisites

*   **Operating System:** Windows 10/11 or Linux (Ubuntu 20.04+ recommended).
*   **Python:** Version 3.11 or higher.
*   **Admin Privileges:** Required only for "Deep Capture" mode (to inspect packets directly). "Basic Mode" works without admin rights.

## 📥 Installation & Setup

### 1. Clone the Repository
Download the source code to your local machine:
```bash
git clone <repository_url>
cd network_monitor
```

### 2. Set Up Virtual Environment (Recommended)
It's best to run Python apps in an isolated environment.

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 4. Optional: Deep Capture Support
For detailed packet inspection (Deep Mode), you need additional drivers:

*   **Windows:** Download and install [Npcap](https://nmap.org/npcap/). Ensure you check "Install Npcap in WinPcap API-compatible Mode".
*   **Linux:** Install eBPF tools:
    ```bash
    sudo apt install python3-bcc
    pip install bcc
    ```

## ▶️ Running the Application

To start the application, simply run:

```bash
python run.py
```

The application window should appear immediately.

## 🖥 Using the Application

### Dashboard
The landing page shows high-level metrics:
*   **Total Upload/Download:** Cumulative data transferred this session.
*   **Current Rate:** Real-time speedometer for Upload/Download (Mbps).
*   **Top Hosts:** List of remote servers utilizing the most bandwidth.

### Interfaces Tab
View a list of all detected network adapters (e.g., `Ethernet`, `Wi-Fi`).
*   Toggle specific interfaces on/off.
*   See individual transfer rates for each card.

### Connections Tab
A detailed table of active network flows:
*   **Process:** Which application is communicating.
*   **Remote Address:** IP/Hostname of the destination.
*   **Protocol:** TCP/UDP.
*   **State:** Established, Time_Wait, etc.

### Settings
Configure the application behavior:
*   **Sampling Interval:** How often to update stats (default: 1000ms). Lower values = more CPU usage but smoother graphs.
*   **Data Retention:** How long to keep history (default: 7 days).
*   **Monitoring Mode:**
    *   *Basic:* Uses OS counters (low overhead, no admin needed).
    *   *Deep:* Inspects packets (high detail, requires admin/Npcap).
*   **Privacy:** Options to mask hostnames or limit storage.

## 🏗 Building Executables

You can compile the application into a standalone `.exe` file that doesn't require Python to run.

**Quick Build (Testing):**
```bash
pip install PyInstaller
pyinstaller pyinstaller_build.spec
```
The executable will be in `dist/NetworkMonitor/NetworkMonitor.exe`.

**Secure/Encrypted Build (Production):**
See `EXE_BUILD_GUIDE.md` for instructions on creating an encrypted, licensed executable using PyArmor.

## ❓ Troubleshooting

| Issue | Solution |
|-------|----------|
| **"Module not found"** | Ensure you activated the venv and ran `pip install -r requirements.txt`. |
| **"Run as Admin" warning** | You are in Basic Mode. For deep packet inspection, restart the terminal/IDE as Administrator. |
| **Deep Mode not working** | **Windows**: Install [Npcap](https://nmap.org/npcap/). **Linux**: Install BCC tools. |
| **Graph is empty** | Check if the correct network interface is selected in Settings. |
| **App won't start** | Verify you are using Python 3.11+. Check console output for errors. |

---
*Generated for Network Monitor Project*
