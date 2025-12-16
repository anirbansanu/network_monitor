# tests/__init__.py
"""
Test suite for Network Monitor application.
Contains unit tests for core logic: aggregator, rate calculator, repository.
"""

import sys
from pathlib import Path

# Add parent directory to path so imports work
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

__all__ = []
