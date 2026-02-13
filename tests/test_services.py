# Tests for backend/services.py — shared service registry
"""
Verify that the centralized service registry provides correct singleton
instances and shared state dicts with the expected shape.
"""

import importlib
import pytest


@pytest.fixture()
def services():
    """Import services module fresh."""
    import backend.services as svc
    return svc


# ---------------------------------------------------------------------------
# Singleton analyzer instances
# ---------------------------------------------------------------------------

class TestSingletonInstances:
    """Verify that services exports the correct analyzer singletons."""

    def test_dashboard_analyzer_type(self, services):
        from analysis.dashboard import DashboardAnalyzer
        assert isinstance(services.dashboard_analyzer, DashboardAnalyzer)

    def test_lag_analyzer_type(self, services):
        from analysis.lag_analysis import LagAnalyzer
        assert isinstance(services.lag_analyzer, LagAnalyzer)

    def test_perf_analyzer_type(self, services):
        from analysis.performance import PerformanceAnalyzer
        assert isinstance(services.perf_analyzer, PerformanceAnalyzer)

    def test_scurve_gen_type(self, services):
        from analysis.scurve import SCurveGenerator
        assert isinstance(services.scurve_gen, SCurveGenerator)

    def test_singletons_are_same_object_across_imports(self):
        """Two imports of services should yield the same object (singleton)."""
        from backend.services import dashboard_analyzer as a1
        from backend.services import dashboard_analyzer as a2
        assert a1 is a2


# ---------------------------------------------------------------------------
# Shared mutable state shape
# ---------------------------------------------------------------------------

class TestParsingState:
    """Verify parsing_state dict has the expected keys and defaults."""

    def test_has_required_keys(self, services):
        required = {"in_progress", "progress", "current_file", "total_files", "records", "max_week"}
        assert required.issubset(services.parsing_state.keys())

    def test_default_values(self, services):
        ps = services.parsing_state
        assert ps["in_progress"] is False
        assert ps["progress"] == 0
        assert ps["current_file"] == ""
        assert ps["total_files"] == 0
        assert ps["records"] == []
        assert ps["max_week"] == 0


class TestManpowerState:
    """Verify manpower_state dict has the expected keys and defaults."""

    def test_has_required_keys(self, services):
        required = {"records", "total_files"}
        assert required.issubset(services.manpower_state.keys())

    def test_default_values(self, services):
        ms = services.manpower_state
        assert ms["records"] == []
        assert ms["total_files"] == 0


class TestSearchState:
    """Verify search_state dict has the expected keys and defaults."""

    def test_has_required_keys(self, services):
        required = {"results", "keyword", "total_files", "matched_files"}
        assert required.issubset(services.search_state.keys())

    def test_default_values(self, services):
        ss = services.search_state
        assert ss["results"] == []
        assert ss["keyword"] == ""
        assert ss["total_files"] == 0
        assert ss["matched_files"] == 0


# ---------------------------------------------------------------------------
# Router imports from services (not local state)
# ---------------------------------------------------------------------------

class TestRouterImportsFromServices:
    """Verify routers reference the shared services state, not local copies."""

    def test_parse_router_uses_services_state(self, services):
        from backend.routers.parse import parsing_state as router_ps
        assert router_ps is services.parsing_state

    def test_manpower_router_uses_services_state(self, services):
        from backend.routers.manpower import manpower_state as router_ms
        assert router_ms is services.manpower_state

    def test_keyword_router_uses_services_state(self, services):
        from backend.routers.keyword import search_state as router_ss
        assert router_ss is services.search_state

    def test_dashboard_router_uses_services_analyzer(self, services):
        from backend.routers.dashboard import analyzer
        assert analyzer is services.dashboard_analyzer

    def test_lag_router_uses_services_analyzer(self, services):
        from backend.routers.lag import lag_analyzer
        assert lag_analyzer is services.lag_analyzer

    def test_performance_router_uses_services_analyzer(self, services):
        from backend.routers.performance import perf_analyzer
        assert perf_analyzer is services.perf_analyzer

    def test_scurve_router_uses_services_generator(self, services):
        from backend.routers.scurve import scurve_gen
        assert scurve_gen is services.scurve_gen


# ---------------------------------------------------------------------------
# Logger presence
# ---------------------------------------------------------------------------

class TestLoggerPresence:
    """Verify all routers and services have a logger configured."""

    @pytest.mark.parametrize("module_path", [
        "backend.services",
        "backend.routers.config",
        "backend.routers.parse",
        "backend.routers.dashboard",
        "backend.routers.lag",
        "backend.routers.performance",
        "backend.routers.scurve",
        "backend.routers.export",
        "backend.routers.keyword",
        "backend.routers.manpower",
    ])
    def test_module_has_logger(self, module_path):
        mod = importlib.import_module(module_path)
        assert hasattr(mod, "logger"), f"{module_path} missing logger"
        assert mod.logger.name == module_path
