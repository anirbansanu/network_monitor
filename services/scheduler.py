# services/scheduler.py
"""
Task scheduler for recurring sampling and cleanup operations.
Uses QTimer for integration with Qt event loop.
"""

from typing import Callable, Optional
from PySide6.QtCore import QTimer, QObject, Signal


class Scheduler(QObject):
    """
    Manages recurring tasks in the Qt event loop.
    """
    
    # Signals
    sample_requested = Signal()  # Emitted when sampling should occur
    cleanup_requested = Signal()  # Emitted when cleanup should occur
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.sample_timer = QTimer(self)
        self.sample_timer.timeout.connect(self._on_sample_timeout)
        
        self.cleanup_timer = QTimer(self)
        self.cleanup_timer.timeout.connect(self._on_cleanup_timeout)
    
    def start_sampling(self, interval_ms: int) -> None:
        """Start periodic sampling."""
        self.sample_timer.start(interval_ms)
    
    def stop_sampling(self) -> None:
        """Stop periodic sampling."""
        self.sample_timer.stop()
    
    def start_cleanup(self, interval_ms: int = 60000) -> None:
        """Start periodic cleanup (default: every 60 seconds)."""
        self.cleanup_timer.start(interval_ms)
    
    def stop_cleanup(self) -> None:
        """Stop cleanup timer."""
        self.cleanup_timer.stop()
    
    def _on_sample_timeout(self):
        """Internal: emit sample request."""
        self.sample_requested.emit()
    
    def _on_cleanup_timeout(self):
        """Internal: emit cleanup request."""
        self.cleanup_requested.emit()
