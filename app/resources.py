# app/resources.py
"""
Application resources manager.
Handles icons, images, and other media assets.
"""

from pathlib import Path
from PySide6.QtGui import QIcon, QPixmap


class AppResources:
    """
    Centralized resource management.
    """
    
    _resource_dir = Path(__file__).parent / "resources"
    
    @classmethod
    def get_app_icon(cls) -> QIcon:
        """Get the application icon."""
        icon_path = cls._resource_dir / "app_icon.png"
        if icon_path.exists():
            return QIcon(str(icon_path))
        return QIcon()
    
    @classmethod
    def get_icon_pixmap(cls, size: int = 256) -> QPixmap:
        """Get icon as pixmap with specified size."""
        icon_path = cls._resource_dir / "app_icon.png"
        if icon_path.exists():
            pixmap = QPixmap(str(icon_path))
            return pixmap.scaledToWidth(size, 0)
        return QPixmap()
