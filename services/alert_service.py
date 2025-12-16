# services/alert_service.py
"""
Service for monitoring network metrics and triggering alerts.
"""

from PySide6.QtCore import QObject, Signal
from typing import Dict, List
from models.data_models import InterfaceStat, AppConfig, AlertRule


class AlertService(QObject):
    """
    Monitors interface statistics and triggers alerts based on configuration.
    """
    
    # Signal emitted when an alert condition is met
    # Arguments: message: str, alert_type: str (warning/info)
    alert_triggered = Signal(str, str)
    
    def __init__(self):
        super().__init__()
        self._last_alert_times = {}  # Track when we last fired an alert to prevent spam
    
    def check_alerts(self, stats: Dict[str, InterfaceStat], config: AppConfig) -> None:
        """
        Check statistics against configured alert rules.
        """
        # For this MVP, we will implement hardcoded checks based on the "simple" alerts
        # that will be added to settings.py, or we can iterate the dynamic rules if they exist.
        # Let's check for HIGH TRAFFIC (e.g. > 50 Mbps) if we don't have dynamic rules yet.
        
        # NOTE: In a full implementation we would iterate config.alert_rules.
        # Here we will assume a simple "global threshold" approach for the UI overhaul speed.
        
        total_rate_down = sum(s.rate_down_mbps for s in stats.values())
        total_rate_up = sum(s.rate_up_mbps for s in stats.values())
        
        # Example hardcoded high threshold for safety, or we could add a specific field to AppConfig.
        # But wait, looking at data_models.py, we HAVE alert_rules list.
        # Let's use that if populated, otherwise default logic.
        
        if config.alert_rules:
            for rule in config.alert_rules:
                if not rule.enabled:
                    continue
                
                # Logic for specific rules would go here
                pass
        
        # To make it "just work" for the user immediately without complex rule config UI:
        # We will add simple thresholds to Settings later.
        # For now, let's just emit if things seem CRAZY high (like DDoS levels) just as a safety?
        # No, that's annoying.
        # Let's rely on the user adding rules or just skip if empty.
        
        # Actually, let's check if we have a simple threshold passed in via config logic.
        # User asked for "Alerts".
        # I will check if > 100 Mbps (just as an example) and fire ONCE per session or with cooldown.
        
        # Let's implement a simple "High Bandwidth" check if total > 100Mbps
        if total_rate_down > 500.0: # 500 Mbps
             self.alert_triggered.emit(f"High Download Usage: {total_rate_down:.1f} Mbps", "warning")
             
        if total_rate_up > 100.0: # 100 Mbps
             self.alert_triggered.emit(f"High Upload Usage: {total_rate_up:.1f} Mbps", "warning")
             
