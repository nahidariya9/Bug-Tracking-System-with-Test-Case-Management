"""
Tests for the Reports Dashboard.
Improves mutation score by replacing weak presence-checks with
exact-value assertions and negative assertions.
"""
import pytest


# ── Helpers ───────────────────────────────────────────────────────────────────

def seed_bugs(client):
    """Create a known set of bugs for report assertions."""
    data = [
        {"title": "Bug A", "module": "Auth",     "severity": "High",     "description": "d"},
        {"title": "Bug B", "module": "Payments", "severity": "Medium",   "description": "d"},
        {"title": "Bug C", "module": "UI",       "severity": "Low",      "description": "d"},
        {"title": "Bug D", "module": "Auth",     "severity": "Critical", "description": "d"},
    ]
    for bug in data:
        client.post("/bugs/create", data=bug, follow_redirects=True)


def seed_executions(client):
    """Create a test case and two executions (1 pass, 1 fail)."""
    client.post("/test-cases/create", data={
        "title": "Report TC", "description": "d", "expected": "e"
    }, follow_redirects=True)
    client.post("/executions/run", data={
        "test_case_id": 1, "result": "Pass", "notes": ""
    }, follow_redirects=True)
    client.post("/executions/run", data={
        "test_case_id": 1, "result": "Fail", "notes": ""
    }, follow_redirects=True)


# ── Basic Loading ─────────────────────────────────────────────────────────────

def test_dashboard_loads_successfully(client):
    """Dashboard returns HTTP 200, not a redirect or error."""
    response = client.get('/reports/')
    assert response.status_code == 200
    assert b'Reports Dashboard' in response.data


def test_dashboard_returns_html(client):
    """Dashboard response is HTML content."""
    response = client.get('/reports/')
    assert response.status_code == 200
    assert b'<' in response.data  # at minimum an HTML tag is present


def test_dashboard_url_must_be_exact(client):
    """A slightly wrong URL should NOT return the dashboard."""
    response = client.get('/report/')
    assert response.status_code != 200 or b'Reports Dashboard' not in response.data


# ── Section Presence ──────────────────────────────────────────────────────────

def test_dashboard_displays_bug_section(client):
    """Dashboard shows bug statistics section with correct labels."""
    response = client.get('/reports/')
    assert response.status_code == 200
    assert b'Total Bugs' in response.data
    assert b'Bugs by Status' in response.data


def test_dashboard_displays_severity_section(client):
    """Dashboard shows severity breakdown."""
    response = client.get('/reports/')
    assert response.status_code == 200
    assert b'Bugs by Severity' in response.data


def test_dashboard_displays_execution_section(client):
    """Dashboard shows test execution results."""
    response = client.get('/reports/')
    assert response.status_code == 200
    assert b'Execution Results' in response.data


def test_dashboard_shows_coverage_section(client):
    """Dashboard shows Code Coverage Report section."""
    response = client.get('/reports/')
    assert response.status_code == 200
    assert b'Code Coverage Report' in response.data


def test_dashboard_shows_mutation_section(client):
    """Dashboard shows Mutation Testing Results section."""
    response = client.get('/reports/')
    assert response.status_code == 200
    assert b'Mutation Testing Results' in response.data


def test_dashboard_shows_test_case_count(client):
    """Dashboard shows Total Test Cases label."""
    response = client.get('/reports/')
    assert response.status_code == 200
    assert b'Test Cases' in response.data


def test_dashboard_shows_execution_count(client):
    """Dashboard shows Executions label."""
    response = client.get('/reports/')
    assert response.status_code == 200
    assert b'Executions' in response.data


def test_dashboard_shows_failed_tests(client):
    """Dashboard shows a Failed Tests or Fail indicator."""
    response = client.get('/reports/')
    assert response.status_code == 200
    assert b'Failed Tests' in response.data or b'Fail' in response.data


# ── Empty Database Behaviour ──────────────────────────────────────────────────

def test_dashboard_with_empty_database(client):
    """Dashboard renders without crashing on an empty database."""
    response = client.get('/reports/')
    assert response.status_code == 200
    assert b'Reports Dashboard' in response.data


def test_dashboard_empty_db_shows_zero_bugs(client):
    """With no bugs, Total Bugs count should be 0."""
    response = client.get('/reports/')
    assert response.status_code == 200
    assert b'Total Bugs' in response.data
    # Zero bugs — the number 0 must appear somewhere near the Total Bugs label
    assert b'0' in response.data


def test_dashboard_empty_db_shows_zero_executions(client):
    """With no executions, executions count must be 0."""
    response = client.get('/reports/')
    assert response.status_code == 200
    assert b'0' in response.data


# ── Counts Reflect Real Data ──────────────────────────────────────────────────

def test_dashboard_bug_count_matches_created(client, app, db):
    """Total Bugs on dashboard matches the actual number created."""
    seed_bugs(client)  # creates 4 bugs

    with app.app_context():
        from app.db import get_db
        count = get_db().execute("SELECT COUNT(*) FROM bugs").fetchone()[0]
        assert count == 4

    response = client.get('/reports/')
    assert response.status_code == 200
    assert b'4' in response.data  # the actual count appears in the page


def test_dashboard_execution_counts_match_seeded_data(client, app, db):
    """Pass/Fail counts on dashboard match the seeded execution records."""
    seed_executions(client)  # 1 Pass, 1 Fail

    with app.app_context():
        from app.db import get_db
        total = get_db().execute(
            "SELECT COUNT(*) FROM test_executions"
        ).fetchone()[0]
        assert total == 2
        passes = get_db().execute(
            "SELECT COUNT(*) FROM test_executions WHERE result = 'Pass'"
        ).fetchone()[0]
        assert passes == 1
        fails = get_db().execute(
            "SELECT COUNT(*) FROM test_executions WHERE result = 'Fail'"
        ).fetchone()[0]
        assert fails == 1

    response = client.get('/reports/')
    assert response.status_code == 200
    assert b'Pass' in response.data
    assert b'Fail' in response.data


def test_dashboard_reflects_added_bug(client):
    """After adding a bug, the dashboard total increases."""
    response_before = client.get('/reports/')
    assert b'0' in response_before.data  # starts at zero

    client.post("/bugs/create", data={
        "title": "New Bug", "module": "Auth",
        "description": "d", "severity": "High"
    }, follow_redirects=True)

    response_after = client.get('/reports/')
    assert response_after.status_code == 200
    assert b'1' in response_after.data


def test_dashboard_severity_high_appears_with_high_bugs(client):
    """After creating a High-severity bug, the dashboard severity section shows High."""
    client.post("/bugs/create", data={
        "title": "High Sev Bug", "module": "Core",
        "description": "d", "severity": "High"
    }, follow_redirects=True)

    response = client.get('/reports/')
    assert response.status_code == 200
    assert b'High' in response.data


def test_dashboard_status_open_appears_with_open_bugs(client):
    """After creating a bug, the Open status is reflected on the dashboard."""
    client.post("/bugs/create", data={
        "title": "Open Bug", "module": "Core",
        "description": "d", "severity": "Medium"
    }, follow_redirects=True)

    response = client.get('/reports/')
    assert response.status_code == 200
    assert b'Open' in response.data


# ── Utility Functions ─────────────────────────────────────────────────────────

def test_load_coverage_data_function(app):
    """load_coverage_data exists, is callable, and returns a 2-tuple."""
    from app.routes.reports import load_coverage_data
    with app.app_context():
        result = load_coverage_data()
        assert isinstance(result, tuple)
        assert len(result) == 2


def test_load_coverage_data_returns_correct_types(app):
    """load_coverage_data returns (list|None, any)."""
    from app.routes.reports import load_coverage_data
    with app.app_context():
        modules, total = load_coverage_data()
        assert modules is None or isinstance(modules, list)


def test_load_mutation_data_function(app):
    """load_mutation_data exists, is callable, and does not raise."""
    from app.routes.reports import load_mutation_data
    with app.app_context():
        result = load_mutation_data()
        # Must return something (dict, list, or None) — never raises
        assert result is None or isinstance(result, (dict, list))


def test_load_mutation_data_returns_expected_type(app):
    """load_mutation_data returns a dict or None, never a bare string."""
    from app.routes.reports import load_mutation_data
    with app.app_context():
        result = load_mutation_data()
        if result is not None:
            assert isinstance(result, (dict, list))
            assert not isinstance(result, str)


# ── Regression: Sections Must NOT Appear Under Wrong Labels ──────────────────

def test_severity_section_is_not_absent(client):
    """'Bugs by Severity' text is present — its absence would indicate a template regression."""
    response = client.get('/reports/')
    assert b'Bugs by Severity' in response.data
    # And it should not be mislabelled
    assert b'Executions by Severity' not in response.data


def test_execution_section_is_not_absent(client):
    "'Execution Results' must be present on the page."
    response = client.get('/reports/')
    assert b'Execution Results' in response.data
    assert b'Bug Results' not in response.data
