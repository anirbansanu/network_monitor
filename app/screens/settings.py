# app/screens/settings.py
"""
Settings screen for application configuration.
"""

from typing import List, Callable
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
    QCheckBox, QComboBox, QPushButton, QGroupBox, QListWidget, QListWidgetItem,
    QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt

from models.data_models import AppConfig
from services.permission_service import PermissionService
from services.export_service import ExportService
# Import internal to avoid circular reference if needed, or pass repository
from storage.repository import Repository



class SettingsScreen(QWidget):
    """
    Application settings and configuration.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.on_config_changed: Callable = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        
        # ===== Sampling =====
        sampling_group = QGroupBox("Sampling")
        sampling_layout = QVBoxLayout()
        
        sampling_label = QLabel("Sampling Interval (ms):")
        self.sampling_spinbox = QSpinBox()
        self.sampling_spinbox.setMinimum(100)
        self.sampling_spinbox.setMaximum(10000)
        self.sampling_spinbox.setValue(1000)
        self.sampling_spinbox.setSuffix(" ms")
        
        sampling_inner = QHBoxLayout()
        sampling_inner.addWidget(sampling_label)
        sampling_inner.addWidget(self.sampling_spinbox)
        sampling_layout.addLayout(sampling_inner)
        sampling_group.setLayout(sampling_layout)
        layout.addWidget(sampling_group)
        
        # ===== Data Retention =====
        retention_group = QGroupBox("Data Retention")
        retention_layout = QVBoxLayout()
        
        retention_label = QLabel("Retention Period (days):")
        self.retention_spinbox = QSpinBox()
        self.retention_spinbox.setMinimum(1)
        self.retention_spinbox.setMaximum(365)
        self.retention_spinbox.setValue(30)
        self.retention_spinbox.setSuffix(" days")
        
        retention_inner = QHBoxLayout()
        retention_inner.addWidget(retention_label)
        retention_inner.addWidget(self.retention_spinbox)
        retention_layout.addLayout(retention_inner)
        retention_group.setLayout(retention_layout)
        layout.addWidget(retention_group)
        
        # ===== Capture Mode =====
        capture_group = QGroupBox("Network Capture")
        capture_layout = QVBoxLayout()
        
        self.deep_capture_checkbox = QCheckBox("Enable Deep Packet Capture (Npcap/eBPF)")
        capture_mode_label = QLabel("Capture Mode Status:")
        self.capture_status_label = QLabel("Basic Mode (No Admin)")
        self.capture_status_label.setStyleSheet("color: #999;")
        
        capture_layout.addWidget(self.deep_capture_checkbox)
        capture_layout.addWidget(capture_mode_label)
        capture_layout.addWidget(self.capture_status_label)
        capture_group.setLayout(capture_layout)
        layout.addWidget(capture_group)
        
        # ===== Interface Selection =====
        interface_group = QGroupBox("Monitor Interfaces")
        interface_layout = QVBoxLayout()
        
        interface_label = QLabel("Select interfaces to monitor (empty = all):")
        self.interface_list = QListWidget()
        self.interface_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        
        interface_layout.addWidget(interface_label)
        interface_layout.addWidget(self.interface_list)
        interface_group.setLayout(interface_layout)
        layout.addWidget(interface_group)
        
        # ===== Privacy =====
        privacy_group = QGroupBox("Privacy")
        privacy_layout = QVBoxLayout()
        
        self.privacy_hostname_checkbox = QCheckBox("Don't store hostnames")
        self.privacy_limit_checkbox = QCheckBox("Limit retention per privacy settings")
        
        privacy_layout.addWidget(self.privacy_hostname_checkbox)
        privacy_group.setLayout(privacy_layout)
        layout.addWidget(privacy_group)

        # ===== Data Management (Export) =====
        data_group = QGroupBox("Data Management")
        data_layout = QHBoxLayout()
        
        self.export_btn = QPushButton("Export Connection History (CSV)")
        self.export_btn.clicked.connect(self._export_data)
        
        data_layout.addWidget(self.export_btn)
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)

        
        # ===== Actions =====
        actions_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self._on_save)
        
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.setObjectName("secondary")
        self.reset_button.clicked.connect(self._on_reset)
        
        actions_layout.addWidget(self.save_button)
        actions_layout.addWidget(self.reset_button)
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        layout.addStretch()
    
    def load_config(self, config: AppConfig) -> None:
        """Load configuration into UI."""
        self.sampling_spinbox.setValue(config.sampling_interval_ms)
        self.retention_spinbox.setValue(config.retention_days)
        self.deep_capture_checkbox.setChecked(config.deep_capture_enabled)
        self.privacy_hostname_checkbox.setChecked(config.privacy_no_hostname)
        self.privacy_limit_checkbox.setChecked(config.privacy_limit_retention)
    
    def set_available_interfaces(self, interfaces: List[str]) -> None:
        """Populate available interfaces."""
        self.interface_list.clear()
        for iface in interfaces:
            item = QListWidgetItem(iface)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            self.interface_list.addItem(item)
    
    def update_capture_status(self, capabilities: dict) -> None:
        """Update capture status display."""
        if capabilities["deep_capture_possible"]:
            status_text = "✓ Deep Capture Available"
            self.capture_status_label.setStyleSheet("color: #0dbfb8;")
        else:
            if capabilities["platform"] == "win32":
                status_text = "✗ Deep Capture Unavailable (Npcap required)"
            else:
                status_text = "✗ Deep Capture Unavailable (eBPF/root required)"
            self.capture_status_label.setStyleSheet("color: #ff6b6b;")
        
        self.capture_status_label.setText(status_text)
        self.deep_capture_checkbox.setEnabled(capabilities["deep_capture_possible"])
    
    def _on_save(self):
        """Handle save button click."""
        if self.on_config_changed:
            selected_interfaces = [
                self.interface_list.item(i).text()
                for i in range(self.interface_list.count())
                if self.interface_list.item(i).checkState() == Qt.CheckState.Checked
            ]
            
            config = AppConfig(
                sampling_interval_ms=self.sampling_spinbox.value(),
                retention_days=self.retention_spinbox.value(),
                deep_capture_enabled=self.deep_capture_checkbox.isChecked(),
                interface_selection=selected_interfaces,
                privacy_no_hostname=self.privacy_hostname_checkbox.isChecked(),
                privacy_limit_retention=self.privacy_limit_checkbox.isChecked(),
            )
            
            self.on_config_changed(config)
    
    def _on_reset(self):
        """Reset to defaults."""
        self.sampling_spinbox.setValue(1000)
        self.retention_spinbox.setValue(30)
        self.deep_capture_checkbox.setChecked(False)
        self.privacy_hostname_checkbox.setChecked(False)
        self.privacy_limit_checkbox.setChecked(True)

    def _export_data(self):
        """Export data to CSV."""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Data", "network_monitor_export.csv", "CSV Files (*.csv)"
        )
        
        if not filepath:
            return
            
        # We need access to repository to get data. 
        # Ideally, we should request this via a service or callback.
        # For MVP, let's create a temporary repository instance to fetch data.
        try:
            repo = Repository()
            flows = repo.get_all_flows() # We need to make sure this method exists
            
            if not flows:
                 QMessageBox.information(self, "Export", "No data to export.")
                 return
                 
            success = ExportService.export_flows_to_csv(filepath, flows)
            
            if success:
                QMessageBox.information(self, "Export", f"Data exported to {filepath}")
            else:
                QMessageBox.warning(self, "Export", "Failed to export data.")
                
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

