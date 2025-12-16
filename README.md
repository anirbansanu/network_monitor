# Network Monitor - Cross-Platform Desktop App

A modern, production-ready Python desktop application for real-time network monitoring. Shows live upload/download rates, per-interface statistics, active connections, and historical trends.

## Features

- **Real-Time Dashboard**: KPI cards, live Mbps charts, top remote hosts
- **Interface Monitoring**: Per-NIC upload/download totals and current rates
- **Connection Tracking**: Active flows with 5-tuple info (protocol, IPs, ports)
- **Configurable Settings**: Sampling interval, retention days, capture mode, privacy options
- **Two Monitoring Modes**:
  - **Basic Mode** (no admin): Uses `psutil` for interface-level counters
  - **Deep Mode** (admin + driver): Windows Npcap or Linux eBPF for packet capture
- **Modern UI**: Dark theme, responsive layout, search/filter capabilities
- **Data Persistence**: SQLite time-series storage with configurable retention

## System Requirements

- **Python**: 3.11 or higher
- **OS**: Windows 10+ or Linux (Ubuntu 20.04+)
- **Admin privileges**: Required for deep packet capture (Npcap/eBPF)

## Installation

### 1. Clone and Setup

```bash
git clone <repo_url>
cd network_monitor
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate



Application Architecture

network_monitor/
├── app/                  # Qt UI (PySide6)
│   ├── main.py          # Main app entry point and worker integration
│   ├── main_window.py   # Main window, sidebar navigation
│   ├── screens/         # Dashboard, Interfaces, Connections, Settings
│   ├── widgets/         # KPI cards, charts, alert banners
│   └── theme/           # QSS dark theme
├── core/                # Business logic
│   ├── network_sampler.py    # psutil-based interface sampling
│   ├── packet_capture.py     # Windows Npcap / Linux eBPF engines
│   ├── aggregator.py         # Flow and host aggregation
│   └── rate_calculator.py    # Rate (Mbps) calculations
├── models/              # Data models (dataclasses)
│   └── data_models.py   # InterfaceStat, FlowStat, HostStat, etc.
├── storage/             # SQLite persistence
│   ├── repository.py    # Data access layer
│   ├── migrations.py    # Schema initialization and migrations
│   └── schema.sql       # SQL schema
├── services/            # High-level services
│   ├── permission_service.py  # Admin/driver detection
│   ├── config_service.py      # Configuration management
│   └── scheduler.py           # Qt-based task scheduler
├── tests/               # Unit tests
│   ├── test_aggregator.py
│   └── test_rate_calculator.py
└── requirements.txt

