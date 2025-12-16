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
                background-color: rgba(211, 47, 47, 0.9);
                border: 1px solid #ff5252;
                border-radius: 4px;
            }
        """)
        
        self.hide()
        self.auto_dismiss_timer = QTimer(self)
        self.auto_dismiss_timer.timeout.connect(self.hide)
    
    def show_warning(self, message: str, duration_ms: int = 5000) -> None:
        """Show a warning banner that auto-dismisses."""
        self.message_label.setText(f"⚠ {message}")
        self.setStyleSheet("""
            AlertBanner {
                background-color: rgba(60, 20, 20, 0.95);
                border: 1px solid #ff5252;
                border-radius: 4px;
            }
        """)
        self.show()
        
        # Auto-dismiss after duration
        self.auto_dismiss_timer.start(duration_ms)
    
    def show_info(self, message: str, duration_ms: int = 5000) -> None:
        """Show an info banner."""
        self.message_label.setText(f"ℹ {message}")
        self.setStyleSheet("""
            AlertBanner {
                background-color: rgba(10, 40, 40, 0.95);
                border: 1px solid #64ffda;
                border-radius: 4px;
            }
        """)
        self.show()
        self.auto_dismiss_timer.start(duration_ms)
