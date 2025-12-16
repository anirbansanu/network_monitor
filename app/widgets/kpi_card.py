# app/widgets/kpi_card.py
"""
KPI card widget for dashboard.
Displays a metric with value and trend.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class KPICard(QWidget):
    """
    A simple KPI card showing a metric name, value, and optional unit.
    """
    
    def __init__(self, title: str, unit: str = "", parent=None):
        super().__init__(parent)
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-size: 12px; color: #999;")
        
        self.value_label = QLabel("0.00")
        self.value_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #0dbfb8;")
        
        self.unit_label = QLabel(unit)
        self.unit_label.setStyleSheet("font-size: 14px; color: #666;")
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.unit_label)
        layout.setSpacing(4)
        layout.setContentsMargins(16, 16, 16, 16)
        
        self.setStyleSheet("""
            KPICard {
                background-color: #2a2a2a;
                border-radius: 8px;
                border: 1px solid #444;
            }
        """)
    
    def set_value(self, value: float) -> None:
        """Update the displayed value."""
        if value >= 1024 * 1024:
            display_value = f"{value / (1024 * 1024):.2f}"
        elif value >= 1024:
            display_value = f"{value / 1024:.2f}"
        else:
            display_value = f"{value:.2f}"
        
        self.value_label.setText(display_value)
