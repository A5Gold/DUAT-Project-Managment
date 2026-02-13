# MTR DUAT - Shared Service Registry
"""
Centralized state management for analyzer instances.
All routers import from here instead of cross-importing from each other.
This decouples router modules and provides a single source of truth.

TD-1 / TD-8: Replaces per-router global singletons with a single registry.
"""

import logging
from typing import Any, Dict, List

from analysis.dashboard import DashboardAnalyzer
from analysis.lag_analysis import LagAnalyzer
from analysis.performance import PerformanceAnalyzer
from analysis.scurve import SCurveGenerator

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Singleton analyzer instances (stateful classes from analysis/)
# ---------------------------------------------------------------------------
dashboard_analyzer = DashboardAnalyzer()
lag_analyzer = LagAnalyzer()
perf_analyzer = PerformanceAnalyzer()
scurve_gen = SCurveGenerator()

# ---------------------------------------------------------------------------
# Shared mutable state for stateless routers
# Shapes match what each router actually reads/writes.
# ---------------------------------------------------------------------------

parsing_state: Dict[str, Any] = {
    "in_progress": False,
    "progress": 0,
    "current_file": "",
    "total_files": 0,
    "records": [],
    "max_week": 0,
}

manpower_state: Dict[str, Any] = {
    "records": [],
    "total_files": 0,
}

search_state: Dict[str, Any] = {
    "results": [],
    "keyword": "",
    "total_files": 0,
    "matched_files": 0,
}
