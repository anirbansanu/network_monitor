# app/widgets/alert_banner.py
"""
Alert banner widget for displaying warnings and notifications.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer
from typing import Optional


class AlertBanner(QWidget):
    """
    A dismissible alert banner for warnings and notifications.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.message_label = QLabel()
        self.message_label.setStyleSheet("color: #fff; font-size: 13px;")
        
        layout = QHBoxLayout(self)
        layout.addWidget(self.message_label)
        layout.setContentsMargins(16, 12, 16, 12)
        
        self.setStyleSheet("""
            AlertBanner {
                background-color: #d32f2f;
                border-radius: 4px;
            }
        """)
        
        self.hide()
        self.auto_dismiss_timer = QTimer(self)
        self.auto_dismiss_timer.timeout.connect(self.hide)
    
    def show_warning(self, message: str, duration_ms: int = 5000) -> None:
        """Show a warning banner that auto-dismisses."""
        self.message_label.setText(message)
        self.show()
        
        # Auto-dismiss after duration
        self.auto_dismiss_timer.start(duration_ms)
    
    def show_info(self, message: str, duration_ms: int = 5000) -> None:
        """Show an info banner."""
        self.message_label.setText(message)
        self.setStyleSheet("""
            AlertBanner {
                background-color: #1976d2;
                border-radius: 4px;
            }
        """)
        self.show()
        self.auto_dismiss_timer.start(duration_ms)
