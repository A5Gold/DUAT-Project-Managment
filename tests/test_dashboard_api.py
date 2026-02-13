# MTR DUAT - Dashboard API Endpoint Tests
"""Integration tests for backend/routers/dashboard.py endpoints."""

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services import dashboard_analyzer


# ---------------------------------------------------------------------------
# Mock data: realistic DOCX-parsed records
# ---------------------------------------------------------------------------

MOCK_RECORDS = [
    # Week 1 - EAL line
    {"FullDate": "Mon 01/01", "Project": "C2264", "Qty Delivered": 5, "Week": "WK01", "Year": "2024", "Line": "EAL"},
    {"FullDate": "Tue 02/01", "Project": "C2264", "Qty Delivered": 3, "Week": "WK01", "Year": "2024", "Line": "EAL"},
    {"FullDate": "Wed 03/01", "Project": "CBM", "Qty Delivered": 2, "Week": "WK01", "Year": "2024", "Line": "EAL"},
    # Week 2 - mixed lines
    {"FullDate": "Thu 08/01", "Project": "C2264", "Qty Delivered": 4, "Week": "WK02", "Year": "2024", "Line": "EAL"},
    {"FullDate": "Fri 09/01", "Project": "PA work", "Qty Delivered": 1, "Week": "WK02", "Year": "2024", "Line": "TWL"},
    {"FullDate": "Sat 10/01", "Project": "Provide", "Qty Delivered": 6, "Week": "WK02", "Year": "2024", "Line": "TWL"},
    # Week 3 - mixed lines
    {"FullDate": "Mon 15/01", "Project": "C2264", "Qty Delivered": 7, "Week": "WK03", "Year": "2024", "Line": "KTL"},
    {"FullDate": "Tue 16/01", "Project": "HLM", "Qty Delivered": 2, "Week": "WK03", "Year": "2024", "Line": "KTL"},
    {"FullDate": "Wed 17/01", "Project": "CM", "Qty Delivered": 3, "Week": "WK03", "Year": "2024", "Line": "EAL"},
    # Week 4 - more variety
    {"FullDate": "Mon 22/01", "Project": "C2264", "Qty Delivered": 5, "Week": "WK04", "Year": "2024", "Line": "EAL"},
    {"FullDate": "Tue 23/01", "Project": "CBM", "Qty Delivered": 4, "Week": "WK04", "Year": "2024", "Line": "TWL"},
    {"FullDate": "Wed 24/01", "Project": "PA work", "Qty Delivered": 2, "Week": "WK04", "Year": "2024", "Line": "KTL"},
]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _reset_analyzer():
    """Reset shared analyzer before each test."""
    dashboard_analyzer.df = None
    dashboard_analyzer.summary = None
    dashboard_analyzer.nth_trend = None
    dashboard_analyzer.last_updated = None
    yield
    dashboard_analyzer.df = None
    dashboard_analyzer.summary = None
    dashboard_analyzer.nth_trend = None
    dashboard_analyzer.last_updated = None


@pytest.fixture
def client():
    """FastAPI TestClient."""
    return TestClient(app)


@pytest.fixture
def loaded_client(client):
    """TestClient with data pre-loaded via the analyze endpoint."""
    res = client.post(
        "/api/dashboard/analyze",
        json={"records": MOCK_RECORDS, "max_week": 4},
    )
    assert res.status_code == 200
    return client


# ---------------------------------------------------------------------------
# POST /api/dashboard/analyze
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestDashboardAnalyze:

    def test_analyze_returns_200(self, client):
        res = client.post(
            "/api/dashboard/analyze",
            json={"records": MOCK_RECORDS, "max_week": 4},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert "stats" in data

    def test_analyze_empty_records_returns_400(self, client):
        res = client.post(
            "/api/dashboard/analyze",
            json={"records": [], "max_week": 4},
        )
        assert res.status_code == 400


# ---------------------------------------------------------------------------
# GET /api/dashboard/stats
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestDashboardStats:

    def test_stats_returns_200(self, loaded_client):
        res = loaded_client.get("/api/dashboard/stats")
        assert res.status_code == 200

    def test_stats_has_expected_keys(self, loaded_client):
        data = loaded_client.get("/api/dashboard/stats").json()
        assert "total_records" in data
        assert "total_nth" in data
        assert "total_qty" in data
        assert "unique_projects" in data

    def test_stats_values_match_mock(self, loaded_client):
        data = loaded_client.get("/api/dashboard/stats").json()
        assert data["total_records"] == len(MOCK_RECORDS)
        # C2264, CBM, PA work, Provide, HLM, CM
        assert data["unique_projects"] == 6

    def test_stats_404_when_no_data(self, client):
        res = client.get("/api/dashboard/stats")
        assert res.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/dashboard/summary
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestDashboardSummary:

    def test_summary_returns_200(self, loaded_client):
        res = loaded_client.get("/api/dashboard/summary")
        assert res.status_code == 200

    def test_summary_has_columns_and_data(self, loaded_client):
        data = loaded_client.get("/api/dashboard/summary").json()
        assert "columns" in data
        assert "data" in data
        assert len(data["data"]) > 0

    def test_summary_404_when_no_data(self, client):
        res = client.get("/api/dashboard/summary")
        assert res.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/dashboard/trends/weekly
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestDashboardWeeklyTrend:

    def test_weekly_returns_200(self, loaded_client):
        res = loaded_client.get("/api/dashboard/trends/weekly")
        assert res.status_code == 200

    def test_weekly_has_labels_and_datasets(self, loaded_client):
        data = loaded_client.get("/api/dashboard/trends/weekly").json()
        assert "labels" in data
        assert "datasets" in data

    def test_weekly_404_when_no_data(self, client):
        res = client.get("/api/dashboard/trends/weekly")
        assert res.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/dashboard/trends/monthly
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestDashboardMonthlyTrend:

    def test_monthly_returns_200(self, loaded_client):
        res = loaded_client.get("/api/dashboard/trends/monthly")
        assert res.status_code == 200

    def test_monthly_has_labels_and_data(self, loaded_client):
        data = loaded_client.get("/api/dashboard/trends/monthly").json()
        assert "labels" in data
        assert "data" in data

    def test_monthly_404_when_no_data(self, client):
        res = client.get("/api/dashboard/trends/monthly")
        assert res.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/dashboard/distribution/projects
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestDashboardProjectDistribution:

    def test_project_dist_returns_200(self, loaded_client):
        res = loaded_client.get("/api/dashboard/distribution/projects")
        assert res.status_code == 200

    def test_project_dist_has_labels_and_data(self, loaded_client):
        data = loaded_client.get("/api/dashboard/distribution/projects").json()
        assert "labels" in data
        assert "data" in data
        assert len(data["labels"]) == len(data["data"])

    def test_project_dist_404_when_no_data(self, client):
        res = client.get("/api/dashboard/distribution/projects")
        assert res.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/dashboard/distribution/keywords
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestDashboardKeywordDistribution:

    def test_keyword_dist_returns_200(self, loaded_client):
        res = loaded_client.get("/api/dashboard/distribution/keywords")
        assert res.status_code == 200

    def test_keyword_dist_has_labels_and_data(self, loaded_client):
        data = loaded_client.get("/api/dashboard/distribution/keywords").json()
        assert "labels" in data
        assert "data" in data

    def test_keyword_dist_404_when_no_data(self, client):
        res = client.get("/api/dashboard/distribution/keywords")
        assert res.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/dashboard/distribution/lines
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestDashboardLineDistribution:

    def test_line_dist_returns_200(self, loaded_client):
        res = loaded_client.get("/api/dashboard/distribution/lines")
        assert res.status_code == 200

    def test_line_dist_has_expected_structure(self, loaded_client):
        data = loaded_client.get("/api/dashboard/distribution/lines").json()
        assert "labels" in data
        assert "nth_data" in data
        assert "qty_data" in data

    def test_line_dist_contains_mock_lines(self, loaded_client):
        data = loaded_client.get("/api/dashboard/distribution/lines").json()
        assert "EAL" in data["labels"]

    def test_line_dist_404_when_no_data(self, client):
        res = client.get("/api/dashboard/distribution/lines")
        assert res.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/dashboard/raw-data
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestDashboardRawData:

    def test_raw_data_returns_200(self, loaded_client):
        res = loaded_client.get("/api/dashboard/raw-data?limit=10&offset=0")
        assert res.status_code == 200

    def test_raw_data_has_pagination(self, loaded_client):
        data = loaded_client.get("/api/dashboard/raw-data?limit=5&offset=0").json()
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert "data" in data
        assert data["total"] == len(MOCK_RECORDS)
        assert len(data["data"]) == 5

    def test_raw_data_offset(self, loaded_client):
        data = loaded_client.get("/api/dashboard/raw-data?limit=5&offset=5").json()
        assert len(data["data"]) == 5
        assert data["offset"] == 5

    def test_raw_data_404_when_no_data(self, client):
        res = client.get("/api/dashboard/raw-data?limit=10&offset=0")
        assert res.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/dashboard/pivot
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestDashboardPivot:

    def test_pivot_returns_200(self, loaded_client):
        res = loaded_client.get("/api/dashboard/pivot")
        assert res.status_code == 200

    def test_pivot_has_columns_and_data(self, loaded_client):
        data = loaded_client.get("/api/dashboard/pivot").json()
        assert "columns" in data
        assert "data" in data

    def test_pivot_404_when_no_data(self, client):
        res = client.get("/api/dashboard/pivot")
        assert res.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/dashboard/trends/nth-by-project
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestDashboardNthByProject:

    def test_nth_by_project_returns_200(self, loaded_client):
        res = loaded_client.get("/api/dashboard/trends/nth-by-project")
        assert res.status_code == 200

    def test_nth_by_project_has_expected_structure(self, loaded_client):
        data = loaded_client.get("/api/dashboard/trends/nth-by-project").json()
        assert "labels" in data
        assert "projects" in data
        assert "datasets" in data
        assert "totals" in data

    def test_nth_by_project_404_when_no_data(self, client):
        res = client.get("/api/dashboard/trends/nth-by-project")
        assert res.status_code == 404
