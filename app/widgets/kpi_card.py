# app/widgets/kpi_card.py
"""
KPI card widget for dashboard.
Displays a metric with value and trend.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class KPICard(QWidget):
    """
    A simple KPI card showing a metric name, value, and optional unit.
    Uses a QFrame internal container for polished styling.
    """
    
    def __init__(self, title: str, unit: str = "", parent=None):
        super().__init__(parent)
        
        # Main layout for the widget
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Container Frame (The visible card)
        self.container = QFrame()
        self.container.setObjectName("kpiCard")
        self.container.setStyleSheet("""
            QFrame#kpiCard {
                background-color: #112240;
                border: 1px solid #233554;
                border-radius: 12px;
            }
            QFrame#kpiCard:hover {
                background-color: #172a45;
                border: 1px solid #64ffda;
            }
        """)
        
        # apply subtle shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)
        
        # Card Layout
        card_layout = QVBoxLayout(self.container)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(8)
        
        # Title
        self.title_label = QLabel(title.upper())
        self.title_label.setStyleSheet("""
            color: #64ffda;
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 1px;
        """)
        
        # Value
        self.value_label = QLabel("0.00")
        self.value_label.setStyleSheet("""
            color: #e6f1ff;
            font-size: 28px;
            font-weight: 600;
        """)
        
        # Unit
        self.unit_label = QLabel(unit)
        self.unit_label.setStyleSheet("color: #8892b0; font-size: 13px;")
        
        card_layout.addWidget(self.title_label)
        card_layout.addWidget(self.value_label)
        card_layout.addWidget(self.unit_label)
        card_layout.addStretch()
        
        self.main_layout.addWidget(self.container)
    
    def set_value(self, value: float) -> None:
        """Update the displayed value."""
        if value >= 1024 * 1024:
            display_value = f"{value / (1024 * 1024):.2f}"
        elif value >= 1024:
            display_value = f"{value / 1024:.2f}"
        else:
            display_value = f"{value:.2f}"
        
        self.value_label.setText(display_value)
