# app/widgets/chart_widget.py
"""
Real-time chart widget using pyqtgraph.
Shows upload/download rates over time.
"""

from typing import Dict, List
from datetime import datetime
from PySide6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg


class ChartWidget(QWidget):
    """
    Real-time line chart for upload/download rates.
    Uses pyqtgraph for efficient rendering.
    """
    
    def __init__(self, max_points: int = 300, parent=None):
        super().__init__(parent)
        self.max_points = max_points
        
        self.plot_widget = pg.PlotWidget(
            title="Network Rate (Mbps)",
            labels={"left": "Rate (Mbps)", "bottom": "Time (s)"}
        )
        
        # Configure plot appearance
        self.plot_widget.setBackground("#1e1e1e")
        self.plot_widget.setLabel('left', 'Rate', units='Mbps', color='#999')
        self.plot_widget.setLabel('bottom', 'Time', units='s', color='#999')
        
        # Add legend
        self.plot_widget.addLegend()
        
        # Upload curve (green)
        self.upload_curve = self.plot_widget.plot(
            pen=pg.mkPen(color=(13, 191, 184), width=2),
            name="Upload"
        )
        
        # Download curve (blue)
        self.download_curve = self.plot_widget.plot(
            pen=pg.mkPen(color=(100, 150, 255), width=2),
            name="Download"
        )
        
        # Data buffers
        self.upload_data: List[float] = []
        self.download_data: List[float] = []
        self.timestamps: List[float] = []
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.setContentsMargins(0, 0, 0, 0)
    
    def add_data_point(self, upload_mbps: float, download_mbps: float) -> None:
        """Add a new data point to the chart."""
        # Use relative time from start
        if not self.timestamps:
            relative_time = 0.0
        else:
            relative_time = self.timestamps[-1] + 1.0
        
        self.timestamps.append(relative_time)
        self.upload_data.append(upload_mbps)
        self.download_data.append(download_mbps)
        
        # Trim to max points
        if len(self.timestamps) > self.max_points:
            self.timestamps.pop(0)
            self.upload_data.pop(0)
            self.download_data.pop(0)
        
        # Update curves
        self.upload_curve.setData(self.timestamps, self.upload_data)
        self.download_curve.setData(self.timestamps, self.download_data)
    
    def clear(self) -> None:
        """Clear all data."""
        self.timestamps.clear()
        self.upload_data.clear()
        self.download_data.clear()
        self.upload_curve.clear()
        self.download_curve.clear()
