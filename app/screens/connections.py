# app/screens/connections.py
"""
Connections/flows screen showing active network connections.
"""

from typing import List
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLineEdit, QLabel, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from models.data_models import FlowStat


class ConnectionsScreen(QWidget):
    """
    Shows active network connections (flows) with byte tracking.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Search bar
        search_label = QLabel("Search & Filter:")
        search_label_font = QFont()
        search_label_font.setBold(True)
        search_label.setFont(search_label_font)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter by IP, port, protocol, or process...")
        self.search_input.setMaximumWidth(500)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border-radius: 4px;
            }
        """)
        self.search_input.textChanged.connect(self._on_search_changed)
        
        search_layout = QVBoxLayout()
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.setSpacing(6)
        layout.addLayout(search_layout)
        
        # Info label
        self.info_label = QLabel("Loading connections...")
        self.info_label.setStyleSheet("color: #0dbfb8; font-size: 12px; font-weight: bold;")
        layout.addWidget(self.info_label)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Protocol", "Local Address", "Remote Address",
            "↑ Upload (KB)", "↓ Download (KB)", "Process", "Start Time", "Duration"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # Better column sizing
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        
        # Set minimum column widths
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 150)
        
        layout.addWidget(self.table)
    
    def update_flows(self, flows: List[FlowStat]) -> None:
        """Update connections table with proper byte values."""
        self.table.setSortingEnabled(False)  # Disable during update
        self.table.setRowCount(len(flows))
        
        if len(flows) == 0:
            self.info_label.setText("⚠ No active connections detected (may require admin/root for full capture)")
            return
        
        # Count by protocol
        tcp_count = sum(1 for f in flows if f.protocol.value == "TCP")
        udp_count = sum(1 for f in flows if f.protocol.value == "UDP")
        total_upload = sum(f.bytes_up for f in flows)
        total_download = sum(f.bytes_down for f in flows)
        
        self.info_label.setText(
            f"📊 {len(flows)} connections | TCP: {tcp_count} | UDP: {udp_count} | "
            f"Total: ↑{total_upload/1024/1024:.2f}MB ↓{total_download/1024/1024:.2f}MB"
        )
        
        for row, flow in enumerate(flows):
            # Protocol
            protocol_item = QTableWidgetItem(flow.protocol.value)
            protocol_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Local address
            local_addr = f"{flow.local_ip}:{flow.local_port}"
            local_item = QTableWidgetItem(local_addr)
            local_item.setFont(self._get_mono_font())
            
            # Remote address
            remote_addr = f"{flow.remote_ip}:{flow.remote_port}"
            remote_item = QTableWidgetItem(remote_addr)
            remote_item.setFont(self._get_mono_font())
            
            # Upload (KB)
            upload_kb = flow.bytes_up / 1024
            upload_item = QTableWidgetItem(f"{upload_kb:.2f}")
            upload_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            # Download (KB)
            download_kb = flow.bytes_down / 1024
            download_item = QTableWidgetItem(f"{download_kb:.2f}")
            download_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            # Process
            process_name = flow.process_name or "-"
            process_item = QTableWidgetItem(process_name)
            
            # Start time
            start_time_item = QTableWidgetItem(flow.start_time.strftime("%H:%M:%S"))
            start_time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Duration
            duration_sec = (datetime.now() - flow.start_time).total_seconds()
            if duration_sec < 60:
                duration_str = f"{int(duration_sec)}s"
            elif duration_sec < 3600:
                mins = int(duration_sec // 60)
                secs = int(duration_sec % 60)
                duration_str = f"{mins}m {secs}s"
            else:
                hours = int(duration_sec // 3600)
                mins = int((duration_sec % 3600) // 60)
                duration_str = f"{hours}h {mins}m"
            
            duration_item = QTableWidgetItem(duration_str)
            duration_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Add to table
            self.table.setItem(row, 0, protocol_item)
            self.table.setItem(row, 1, local_item)
            self.table.setItem(row, 2, remote_item)
            self.table.setItem(row, 3, upload_item)
            self.table.setItem(row, 4, download_item)
            self.table.setItem(row, 5, process_item)
            self.table.setItem(row, 6, start_time_item)
            self.table.setItem(row, 7, duration_item)
        
        self.table.setSortingEnabled(True)
    
    def _on_search_changed(self, text: str):
        """Filter table by search text."""
        text_lower = text.lower()
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text_lower in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)
    
    def _get_mono_font(self) -> QFont:
        """Get monospace font for IPs."""
        font = QFont()
        font.setFamily("Courier New")
        font.setPointSize(9)
        return font
