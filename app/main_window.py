# app/main_window.py
"""
Main application window.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QListWidgetItem, QStackedWidget, QLabel
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtGui import QIcon

from app.screens.dashboard import DashboardScreen
from app.screens.interfaces import InterfacesScreen
from app.screens.connections import ConnectionsScreen
from app.screens.settings import SettingsScreen
from app.widgets.alert_banner import AlertBanner
from app.resources import AppResources


class MainWindow(QMainWindow):
    """
    Main application window with navigation and screen management.
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Network Monitor")
        
        # Set application icon
        app_icon = AppResources.get_app_icon()
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)
        
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        
        # Alert banner
        self.alert_banner = AlertBanner()
        layout.addWidget(self.alert_banner)
        
        # Main content with sidebar
        content_layout = QHBoxLayout()
        
        # Sidebar navigation
        self.sidebar = QListWidget()
        self.sidebar.setMaximumWidth(200)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: #252525;
                border-right: 1px solid #404040;
            }
            QListWidget::item:selected {
                background-color: #0dbfb8;
            }
        """)
        
        sidebar_items = ["Dashboard", "Interfaces", "Connections", "Settings"]
        for item_text in sidebar_items:
            item = QListWidgetItem(item_text)
            self.sidebar.addItem(item)
        
        self.sidebar.itemClicked.connect(self._on_sidebar_clicked)
        
        # Screen stack
        self.stack = QStackedWidget()
        self.dashboard_screen = DashboardScreen()
        self.interfaces_screen = InterfacesScreen()
        self.connections_screen = ConnectionsScreen()
        self.settings_screen = SettingsScreen()
        
        self.stack.addWidget(self.dashboard_screen)
        self.stack.addWidget(self.interfaces_screen)
        self.stack.addWidget(self.connections_screen)
        self.stack.addWidget(self.settings_screen)
        
        content_layout.addWidget(self.sidebar)
        content_layout.addWidget(self.stack, 1)
        
        layout.addLayout(content_layout)
        
        # Apply theme
        self._load_theme()
        
        # Default to dashboard
        self.sidebar.setCurrentRow(0)
    
    def _on_sidebar_clicked(self, item):
        """Handle sidebar navigation."""
        index = self.sidebar.row(item)
        self.stack.setCurrentIndex(index)
    
    def _load_theme(self):
        """Load dark theme QSS."""
        try:
            from pathlib import Path
            theme_path = Path(__file__).parent / "theme" / "dark.qss"
            if theme_path.exists():
                with open(theme_path, 'r') as f:
                    stylesheet = f.read()
                self.setStyleSheet(stylesheet)
        except Exception as e:
            print(f"Warning: Could not load theme: {e}")
    
    def show_alert(self, message: str, alert_type: str = "warning") -> None:
        """Show an alert banner."""
        if alert_type == "warning":
            self.alert_banner.show_warning(message)
        elif alert_type == "info":
            self.alert_banner.show_info(message)
