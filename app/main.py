# app/main.py
"""
Main application entry point.
Integrates UI, business logic, and data persistence.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict

# Ensure project root is in path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QThread, QObject, Signal, Slot

from app.main_window import MainWindow
from app.resources import AppResources
from core.network_sampler import NetworkSampler
from core.aggregator import Aggregator
from core.packet_capture import get_capture_engine
from models.data_models import InterfaceStat, FlowStat, HostStat
from storage.repository import Repository
from services.config_service import ConfigService
from services.permission_service import PermissionService
from services.scheduler import Scheduler
from services.alert_service import AlertService


class MonitorWorker(QObject):
    """
    Background worker that performs sampling and capture.
    Runs in a separate thread.
    """
    
    # Signals
    interfaces_updated = Signal(dict)  # Dict[str, InterfaceStat]
    flows_updated = Signal(list)  # List[FlowStat]
    hosts_updated = Signal(list)  # List[HostStat]
    error_occurred = Signal(str)
    
    def __init__(self, config_service: ConfigService, repository: Repository):
        super().__init__()
        self.config_service = config_service
        self.repository = repository
        
        self.sampler = NetworkSampler()
        self.aggregator = Aggregator()
        self.sampler = NetworkSampler()
        self.aggregator = Aggregator()
        self.capture_engine = get_capture_engine()
        self.alert_service = AlertService()
        
        self.is_running = False
    
    def do_sample(self):
        """Perform a sampling cycle."""
        if not self.is_running:
            return
        
        try:
            # Sample interfaces
            stats = self.sampler.sample()
            
            if stats:
                # Store samples
                self.repository.save_interface_samples_batch(stats)
                
                # Emit signal
                self.interfaces_updated.emit(stats)

                # Check for alerts
                self.alert_service.check_alerts(stats, self.config_service.get_config())

            
            # Sample active connections (psutil)
            connections = self.sampler.get_active_connections()
            if connections:
                for flow in connections:
                    self.aggregator.update_flow(flow)
                
                # Emit flows signal
                self.flows_updated.emit(connections)
            
            # Sample flows from deep capture if enabled
            if self.capture_engine.is_available():
                try:
                    flows = self.capture_engine.get_flows()
                    if flows:
                        for flow in flows:
                            self.aggregator.update_flow(flow)
                        
                        self.repository.save_flows_batch(flows)
                except Exception as e:
                    print(f"Deep capture error: {e}")
            
            # Get aggregated data
            active_flows = self.aggregator.get_active_flows(timeout_sec=300)
            top_hosts = self.aggregator.get_top_hosts(count=5)
            
            # Update flows display (if we have aggregated data)
            if active_flows:
                self.flows_updated.emit(active_flows)
            
            # Update hosts display
            if top_hosts:
                self.hosts_updated.emit(top_hosts)
            
        except Exception as e:
            print(f"Sampling error: {e}")
            self.error_occurred.emit(str(e))
    
    def start_worker(self):
        """Start background monitoring."""
        self.is_running = True
    
    def stop_worker(self):
        """Stop background monitoring."""
        self.is_running = False


class NetworkMonitorApp(QApplication):
    """
    Main application class with icon support.
    """
    
    def __init__(self, argv):
        super().__init__(argv)
        
        # Set application icon
        app_icon = AppResources.get_app_icon()
        if not app_icon.isNull():
            self.setApplicationIcon(app_icon)
        
        # Initialize services and data layer
        self.repository = Repository()
        self.config_service = ConfigService(self.repository)
        
        # Create main window
        self.main_window = MainWindow()
        
        # Worker thread
        self.worker_thread = QThread()
        self.worker = MonitorWorker(self.config_service, self.repository)
        self.worker.moveToThread(self.worker_thread)
        
        # Connect worker signals
        self.worker.interfaces_updated.connect(self._on_interfaces_updated)
        self.worker.flows_updated.connect(self._on_flows_updated)
        self.worker.hosts_updated.connect(self._on_hosts_updated)
        self.worker.error_occurred.connect(self._on_error)
        self.worker.alert_service.alert_triggered.connect(self._on_alert_triggered)

        self.worker.hosts_updated.connect(self._on_hosts_updated)
        self.worker.error_occurred.connect(self._on_error)
        
        # Scheduler
        self.scheduler = Scheduler()
        self.scheduler.sample_requested.connect(self.worker.do_sample)
        
        # Connect settings
        self.main_window.settings_screen.on_config_changed = self._on_config_changed
        
        # Initialize UI
        self._init_ui()
        
        # Start monitoring
        self._start_monitoring()
    
    def _init_ui(self):
        """Initialize UI with current state."""
        # Load config
        config = self.config_service.get_config()
        self.main_window.settings_screen.load_config(config)
        
        # Set available interfaces
        interfaces = self.worker.sampler.get_interface_names()
        self.main_window.settings_screen.set_available_interfaces(interfaces)
        
        # Check capabilities
        capabilities = PermissionService.get_capability_status()
        self.main_window.settings_screen.update_capture_status(capabilities)
        
        # Show warning if admin not available
        if not capabilities["is_admin"] and capabilities["platform"] == "win32":
            self.main_window.show_alert(
                "Running in Basic Mode. Admin rights required for deep packet capture.",
                alert_type="info"
            )
    
    def _start_monitoring(self):
        """Start the monitoring worker thread."""
        config = self.config_service.get_config()
        
        self.worker_thread.start()
        self.worker.start_worker()
        
        # Start sampling (1 second by default)
        self.scheduler.start_sampling(config.sampling_interval_ms)
        
        # Also trigger first sample immediately
        self.worker.do_sample()
    
    def _on_interfaces_updated(self, stats: Dict[str, InterfaceStat]):
        """Handle interface update signal."""
        self.main_window.interfaces_screen.update_interfaces(stats)
        
        # Update dashboard KPIs
        total_sent = sum(s.bytes_sent for s in stats.values())
        total_recv = sum(s.bytes_recv for s in stats.values())
        total_rate_up = sum(s.rate_up_mbps for s in stats.values())
        total_rate_down = sum(s.rate_down_mbps for s in stats.values())
        
        self.main_window.dashboard_screen.update_kpis(
            total_sent, total_recv, total_rate_up, total_rate_down
        )
        self.main_window.dashboard_screen.add_chart_point(total_rate_up, total_rate_down)
    
    def _on_flows_updated(self, flows: list):
        """Handle flows update signal."""
        if flows:
            self.main_window.connections_screen.update_flows(flows)
    
    def _on_hosts_updated(self, hosts: list):
        """Handle hosts update signal."""
        if hosts:
            self.main_window.dashboard_screen.update_top_hosts(hosts)

    def _on_alert_triggered(self, message: str, alert_type: str):
        """Handle alert signal."""
        self.main_window.show_alert(message, alert_type)

    
    def _on_error(self, error_msg: str):
        """Handle error signal."""
        print(f"Error: {error_msg}")
        self.main_window.show_alert(f"Error: {error_msg}", alert_type="warning")
    
    def _on_config_changed(self, new_config):
        """Handle configuration change."""
        self.config_service._config = new_config
        self.repository.save_config(new_config)
        self.scheduler.stop_sampling()
        self.scheduler.start_sampling(new_config.sampling_interval_ms)
        
        self.main_window.show_alert(
            "Settings saved successfully", alert_type="info"
        )
    
    def closeEvent(self, event):
        """Handle application close."""
        print("Shutting down...")
        self.scheduler.stop_sampling()
        self.scheduler.stop_cleanup()
        self.worker.stop_worker()
        self.worker_thread.quit()
        
        # Wait max 2 seconds for thread to finish
        if not self.worker_thread.wait(2000):
            print("Warning: Worker thread did not finish in time, forcing exit.")
            self.worker_thread.terminate()
            
        event.accept()
        super().closeEvent(event)


def main():
    """Main entry point."""
    app = NetworkMonitorApp(sys.argv)
    main_window = app.main_window
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
