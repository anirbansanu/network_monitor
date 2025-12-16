# services/config_service.py
"""
Application configuration management.
"""

from models.data_models import AppConfig
from storage.repository import Repository


class ConfigService:
    """
    Manages application configuration.
    Provides a high-level API over the Repository.
    """
    
    def __init__(self, repository: Repository):
        self.repository = repository
        self._config = repository.get_config()
    
    def get_config(self) -> AppConfig:
        """Get current configuration."""
        return self._config
    
    def set_sampling_interval(self, ms: int) -> None:
        """Set sampling interval in milliseconds."""
        if ms < 100:  # Minimum 100ms
            ms = 100
        self._config.sampling_interval_ms = ms
        self.repository.save_config(self._config)
    
    def set_retention_days(self, days: int) -> None:
        """Set data retention in days."""
        if days < 1:
            days = 1
        self._config.retention_days = days
        self.repository.save_config(self._config)
    
    def set_deep_capture_enabled(self, enabled: bool) -> None:
        """Enable/disable deep packet capture."""
        self._config.deep_capture_enabled = enabled
        self.repository.save_config(self._config)
    
    def set_interface_selection(self, interfaces: list[str]) -> None:
        """Set which interfaces to monitor."""
        self._config.interface_selection = interfaces
        self.repository.save_config(self._config)
    
    def set_privacy_options(self, no_hostname: bool, limit_retention: bool) -> None:
        """Set privacy options."""
        self._config.privacy_no_hostname = no_hostname
        self._config.privacy_limit_retention = limit_retention
        self.repository.save_config(self._config)
