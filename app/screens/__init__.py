# app/screens/__init__.py
"""
Application screens package.
Contains all UI screens: Dashboard, Interfaces, Connections, Settings.
"""

from app.screens.dashboard import DashboardScreen
from app.screens.interfaces import InterfacesScreen
from app.screens.connections import ConnectionsScreen
from app.screens.settings import SettingsScreen

__all__ = [
    "DashboardScreen",
    "InterfacesScreen",
    "ConnectionsScreen",
    "SettingsScreen",
]
