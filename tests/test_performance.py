# MTR DUAT - Performance Analysis Tests
"""Unit tests for analysis/performance.py"""

import pytest
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')

from analysis.performance import (
    calculate_performance_metrics,
    get_recovery_path,
    plot_performance_chart,
    plot_cumulative_progress,
    PerformanceAnalyzer,
)


def _make_performance_df():
    """Helper: build a DataFrame with weekly project data."""
    rows = []
    for week in range(1, 11):
        # C2264 project: 2 NTH per week, varying qty
        for nth in range(2):
            rows.append({
                "Project": "C2264",
                "Year": "2024",
                "Week": str(week),
                "Qty Delivered": 3.0 + (week % 3),
            })
        # CBM job: 1 NTH per week
        rows.append({
            "Project": "CBM",
            "Year": "2024",
            "Week": str(week),
            "Qty Delivered": 2.0,
        })
    return pd.DataFrame(rows)


# ── calculate_performance_metrics ────────────────────────────────────────────


@pytest.mark.unit
class TestCalculatePerformanceMetrics:

    def test_with_sample_data(self):
        df = _make_performance_df()
        metrics = calculate_performance_metrics(df, "C2264", target_productivity=3.0)

        assert metrics != {}
        assert metrics["total_weeks"] == 10
        assert "weekly_data" in metrics

    def test_empty_project_returns_empty(self):
        df = _make_performance_df()
        metrics = calculate_performance_metrics(df, "NONEXISTENT")
        assert metrics == {}

    def test_returns_correct_keys(self):
        df = _make_performance_df()
        metrics = calculate_performance_metrics(df, "C2264")

        expected_keys = {
            "weekly_data", "total_weeks", "weeks_met_target",
            "weeks_missed", "success_rate", "target_productivity",
            "current_pace", "avg_productivity",
        }
        assert expected_keys == set(metrics.keys())

    def test_success_rate_range(self):
        df = _make_performance_df()
        metrics = calculate_performance_metrics(df, "C2264", target_productivity=3.0)
        assert 0 <= metrics["success_rate"] <= 100

    def test_weeks_met_plus_missed_equals_total(self):
        df = _make_performance_df()
        metrics = calculate_performance_metrics(df, "C2264", target_productivity=3.0)
        assert metrics["weeks_met_target"] + metrics["weeks_missed"] == metrics["total_weeks"]

    def test_case_insensitive_project_match(self):
        df = _make_performance_df()
        metrics = calculate_performance_metrics(df, "c2264")
        assert metrics != {}
        assert metrics["total_weeks"] == 10


# ── get_recovery_path ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestGetRecoveryPath:

    def test_with_remaining_weeks(self):
        result = get_recovery_path(
            target_qty=1000, actual_qty=400,
            remaining_weeks=20, current_productivity=25.0,
        )
        assert result["required_weekly"] == 30.0  # 600 / 20
        assert result["required_productivity"] == 30.0

    def test_zero_remaining_weeks_completed(self):
        result = get_recovery_path(
            target_qty=1000, actual_qty=1000,
            remaining_weeks=0, current_productivity=5.0,
        )
        assert result["on_track"] is True
        assert result["required_weekly"] == 0

    def test_zero_remaining_weeks_not_completed(self):
        result = get_recovery_path(
            target_qty=1000, actual_qty=500,
            remaining_weeks=0, current_productivity=5.0,
        )
        assert result["on_track"] is False

    def test_on_track_when_pace_sufficient(self):
        result = get_recovery_path(
            target_qty=1000, actual_qty=800,
            remaining_weeks=10, current_productivity=25.0,
        )
        # required = 200/10 = 20, current = 25 >= 20
        assert result["on_track"] is True

    def test_not_on_track_when_pace_insufficient(self):
        result = get_recovery_path(
            target_qty=1000, actual_qty=200,
            remaining_weeks=10, current_productivity=5.0,
        )
        # required = 800/10 = 80, current = 5 < 80
        assert result["on_track"] is False

    def test_weeks_to_complete_with_zero_productivity(self):
        result = get_recovery_path(
            target_qty=1000, actual_qty=200,
            remaining_weeks=10, current_productivity=0,
        )
        assert result["weeks_to_complete"] is None


# ── PerformanceAnalyzer ──────────────────────────────────────────────────────


@pytest.mark.unit
class TestPerformanceAnalyzer:

    def test_get_available_projects_filters_c_prefix(self):
        df = _make_performance_df()
        # Add a non-C project to verify filtering
        extra = pd.DataFrame([{
            "Project": "HLM", "Year": "2024", "Week": "1", "Qty Delivered": 1.0,
        }])
        df = pd.concat([df, extra], ignore_index=True)
        analyzer = PerformanceAnalyzer(df)
        projects = analyzer.get_available_projects()

        assert "C2264" in projects
        assert "CBM" in projects  # CBM starts with C, so it passes
        assert "HLM" not in projects

    def test_get_available_projects_empty_df(self):
        analyzer = PerformanceAnalyzer(pd.DataFrame())
        assert analyzer.get_available_projects() == []

    def test_analyze_returns_metrics(self):
        df = _make_performance_df()
        analyzer = PerformanceAnalyzer(df)
        result = analyzer.analyze("C2264", target_productivity=3.0)

        assert result != {}
        assert "total_weeks" in result
        assert "success_rate" in result

    def test_analyze_nonexistent_project(self):
        df = _make_performance_df()
        analyzer = PerformanceAnalyzer(df)
        result = analyzer.analyze("NONEXISTENT")
        assert result == {}

    def test_set_data(self):
        analyzer = PerformanceAnalyzer()
        assert analyzer.get_available_projects() == []

        analyzer.set_data(_make_performance_df())
        assert len(analyzer.get_available_projects()) > 0


# ── plot_performance_chart ──────────────────────────────────────────────────


@pytest.mark.unit
class TestPlotPerformanceChart:

    def test_returns_base64_string(self):
        df = _make_performance_df()
        metrics = calculate_performance_metrics(df, "C2264", target_productivity=3.0)
        weekly_data = metrics["weekly_data"]

        result = plot_performance_chart(
            weekly_data, target_productivity=3.0, project_code="C2264"
        )

        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 100  # base64 string should be substantial

    def test_with_output_path_saves_file(self, tmp_path):
        df = _make_performance_df()
        metrics = calculate_performance_metrics(df, "C2264", target_productivity=3.0)
        weekly_data = metrics["weekly_data"]

        output = tmp_path / "perf_chart.png"
        result = plot_performance_chart(
            weekly_data, target_productivity=3.0,
            project_code="C2264", output_path=output
        )

        assert result is None
        assert output.exists()
        assert output.stat().st_size > 0


# ── plot_cumulative_progress ────────────────────────────────────────────────


@pytest.mark.unit
class TestPlotCumulativeProgress:

    def test_returns_base64_string(self):
        df = _make_performance_df()

        result = plot_cumulative_progress(
            df, project_code="C2264", target_qty=500,
            start_year=2024, end_year=2026
        )

        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 100

    def test_with_output_path_saves_file(self, tmp_path):
        df = _make_performance_df()
        output = tmp_path / "cumulative.png"

        result = plot_cumulative_progress(
            df, project_code="C2264", target_qty=500,
            start_year=2024, end_year=2026, output_path=output
        )

        assert result is None
        assert output.exists()
        assert output.stat().st_size > 0

    def test_nonexistent_project_returns_none(self):
        df = _make_performance_df()

        result = plot_cumulative_progress(
            df, project_code="NONEXISTENT", target_qty=500,
            start_year=2024, end_year=2026
        )

        assert result is None


# ── PerformanceAnalyzer.get_weekly_breakdown ────────────────────────────────


@pytest.mark.unit
class TestPerformanceAnalyzerWeeklyBreakdown:

    def test_get_weekly_breakdown_returns_list(self):
        df = _make_performance_df()
        analyzer = PerformanceAnalyzer(df)
        analyzer.analyze("C2264", target_productivity=3.0)

        breakdown = analyzer.get_weekly_breakdown()

        assert isinstance(breakdown, list)
        assert len(breakdown) == 10
        assert "year" in breakdown[0]
        assert "week" in breakdown[0]
        assert "actual" in breakdown[0]
        assert "status" in breakdown[0]
        assert breakdown[0]["status"] in ("met", "missed")

    def test_get_weekly_breakdown_empty_without_analyze(self):
        analyzer = PerformanceAnalyzer()
        breakdown = analyzer.get_weekly_breakdown()
        assert breakdown == []


# ── PerformanceAnalyzer.analyze with recovery path ──────────────────────────


@pytest.mark.unit
class TestPerformanceAnalyzerRecovery:

    def test_analyze_with_recovery_path_params(self):
        df = _make_performance_df()
        analyzer = PerformanceAnalyzer(df)

        result = analyzer.analyze(
            "C2264", target_productivity=3.0,
            target_qty=1000, start_year=2024, end_year=2027
        )

        assert result != {}
        assert "recovery" in result
        assert "required_weekly" in result["recovery"]
        assert "on_track" in result["recovery"]

    def test_analyze_without_recovery_params(self):
        df = _make_performance_df()
        analyzer = PerformanceAnalyzer(df)

        result = analyzer.analyze("C2264", target_productivity=3.0)

        assert result != {}
        assert "recovery" not in result
