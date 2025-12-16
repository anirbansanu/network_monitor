# app/screens/dashboard.py
"""
Dashboard screen showing KPIs, chart, and top hosts.
"""

from typing import Dict, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QScrollArea
)
from PySide6.QtCore import Qt

from app.widgets.kpi_card import KPICard
from app.widgets.chart_widget import ChartWidget
from models.data_models import InterfaceStat, HostStat


class DashboardScreen(QWidget):
    """
    Main dashboard with KPIs, real-time chart, and top hosts.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        main_layout = QVBoxLayout(self)
        
        # ===== KPI Cards Row =====
        kpi_layout = QHBoxLayout()
        
        self.kpi_upload_today = KPICard("Upload Today", "GB")
        self.kpi_download_today = KPICard("Download Today", "GB")
        self.kpi_rate_up = KPICard("Upload Rate", "Mbps")
        self.kpi_rate_down = KPICard("Download Rate", "Mbps")
        
        kpi_layout.addWidget(self.kpi_upload_today)
        kpi_layout.addWidget(self.kpi_download_today)
        kpi_layout.addWidget(self.kpi_rate_up)
        kpi_layout.addWidget(self.kpi_rate_down)
        
        main_layout.addLayout(kpi_layout)
        
        # ===== Chart =====
        chart_label = QLabel("Network Activity")
        chart_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #0dbfb8;")
        main_layout.addWidget(chart_label)
        
        self.chart = ChartWidget()
        main_layout.addWidget(self.chart)
        
        # ===== Top Hosts Table =====
        hosts_label = QLabel("Top Remote Hosts (by bytes)")
        hosts_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #0dbfb8; margin-top: 16px;")
        main_layout.addWidget(hosts_label)
        
        self.hosts_table = QTableWidget()
        self.hosts_table.setColumnCount(4)
        self.hosts_table.setHorizontalHeaderLabels(["IP", "Hostname", "Upload (MB)", "Download (MB)"])
        self.hosts_table.setMaximumHeight(200)
        self.hosts_table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.hosts_table)
        main_layout.addStretch()
    
    def update_kpis(self, upload_bytes: int, download_bytes: int,
                    upload_rate: float, download_rate: float) -> None:
        """Update KPI card values."""
        self.kpi_upload_today.set_value(upload_bytes / (1024**3))
        self.kpi_download_today.set_value(download_bytes / (1024**3))
        self.kpi_rate_up.set_value(upload_rate)
        self.kpi_rate_down.set_value(download_rate)
    
    def add_chart_point(self, upload_mbps: float, download_mbps: float) -> None:
        """Add a point to the chart."""
        self.chart.add_data_point(upload_mbps, download_mbps)
    
    def update_top_hosts(self, hosts: List[HostStat]) -> None:
        """Update the top hosts table."""
        self.hosts_table.setRowCount(len(hosts))
        
        for row, host in enumerate(hosts):
            ip_item = QTableWidgetItem(host.ip)
            hostname_item = QTableWidgetItem(host.hostname or "-")
            upload_mb = host.total_bytes_up / (1024**2)
            download_mb = host.total_bytes_down / (1024**2)
            upload_item = QTableWidgetItem(f"{upload_mb:.2f}")
            download_item = QTableWidgetItem(f"{download_mb:.2f}")
            
            self.hosts_table.setItem(row, 0, ip_item)
            self.hosts_table.setItem(row, 1, hostname_item)
            self.hosts_table.setItem(row, 2, upload_item)
            self.hosts_table.setItem(row, 3, download_item)
