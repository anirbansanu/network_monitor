# app/screens/interfaces.py
"""
Interfaces screen showing per-NIC statistics.
"""

from typing import Dict
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLineEdit, QLabel
)
from PySide6.QtCore import Qt

from models.data_models import InterfaceStat


class InterfacesScreen(QWidget):
    """
    Shows detailed statistics for each network interface.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        
        # Search bar
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter interfaces...")
        self.search_input.setMaximumWidth(300)
        self.search_input.textChanged.connect(self._on_search_changed)
        
        search_layout = QVBoxLayout()
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Interface", "Status", "Upload (MB)", "Download (MB)", 
            "Up Rate (Mbps)", "Down Rate (Mbps)"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        
        layout.addWidget(self.table)
    
    def update_interfaces(self, stats: Dict[str, InterfaceStat]) -> None:
        """Update interface statistics table."""
        self.table.setRowCount(len(stats))
        
        for row, (name, stat) in enumerate(stats.items()):
            name_item = QTableWidgetItem(name)
            status_item = QTableWidgetItem("UP" if stat.is_up else "DOWN")
            upload_mb = stat.bytes_sent / (1024**2)
            download_mb = stat.bytes_recv / (1024**2)
            upload_item = QTableWidgetItem(f"{upload_mb:.2f}")
            download_item = QTableWidgetItem(f"{download_mb:.2f}")
            rate_up_item = QTableWidgetItem(f"{stat.rate_up_mbps:.2f}")
            rate_down_item = QTableWidgetItem(f"{stat.rate_down_mbps:.2f}")
            
            self.table.setItem(row, 0, name_item)
            self.table.setItem(row, 1, status_item)
            self.table.setItem(row, 2, upload_item)
            self.table.setItem(row, 3, download_item)
            self.table.setItem(row, 4, rate_up_item)
            self.table.setItem(row, 5, rate_down_item)
    
    def _on_search_changed(self, text: str):
        """Filter table by search text."""
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                self.table.setRowHidden(row, text.lower() not in item.text().lower())
