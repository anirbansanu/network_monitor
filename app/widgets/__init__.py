# app/widgets/__init__.py
"""
Custom widgets package.
Contains reusable UI components: KPI cards, charts, alert banners.
"""

from app.widgets.kpi_card import KPICard
from app.widgets.chart_widget import ChartWidget
from app.widgets.alert_banner import AlertBanner

__all__ = [
    "KPICard",
    "ChartWidget",
    "AlertBanner",
]
