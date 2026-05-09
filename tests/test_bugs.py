import pytest


# ── Helpers ──────────────────────────────────────────────────────────────────

def create_bug(client, title="Test Bug", module="Auth",
               description="desc", severity="High"):
    return client.post("/bugs/create", data={
        "title":       title,
        "module":      module,
        "description": description,
        "severity":    severity,
    }, follow_redirects=True)


def create_test_case(client):
    client.post("/test-cases/create", data={
        "title":       "Sample Test Case",
        "description": "Some steps",
        "expected":    "Expected outcome",
    }, follow_redirects=True)


# ── Bug Creation ──────────────────────────────────────────────────────────────

class TestBugCreation:

    def test_create_bug_success(self, client):
        """Valid bug is created and appears in list."""
        response = create_bug(client)
        assert response.status_code == 200
        assert b"Test Bug" in response.data
        assert b"Bug created successfully" in response.data

    def test_create_bug_missing_title(self, client):
        """Bug without title is rejected."""
        response = client.post("/bugs/create", data={
            "title":       "",
            "module":      "Auth",
            "description": "test",
            "severity":    "High",
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b"Title is required" in response.data
        # Confirm bug was NOT created
        assert b"Bug created successfully" not in response.data

    def test_create_bug_invalid_severity(self, client):
        """Bug with invalid severity is rejected."""
        response = client.post("/bugs/create", data={
            "title":       "Bad Bug",
            "module":      "Auth",
            "description": "test",
            "severity":    "INVALID",
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b"Invalid severity" in response.data
        assert b"Bug created successfully" not in response.data

    def test_create_bug_duplicate(self, client):
        """Same title + module combination is rejected as duplicate."""
        first = create_bug(client, title="Dup Bug", module="Login")
        assert b"Bug created successfully" in first.data
        response = create_bug(client, title="Dup Bug", module="Login")
        assert b"already exists" in response.data
        assert b"Bug created successfully" not in response.data

    def test_create_bug_different_module_allowed(self, client):
        """Same title but different module is allowed."""
        create_bug(client, title="Same Title", module="Login")
        response = create_bug(client, title="Same Title", module="Dashboard")
        assert response.status_code == 200
        assert b"Bug created successfully" in response.data
        assert b"already exists" not in response.data

    def test_create_bug_linked_to_test_case(self, client, app):
        """Bug can be created with a test_case_id link."""
        create_test_case(client)
        response = client.post("/bugs/create", data={
            "title":        "Linked Bug",
            "module":       "Auth",
            "description":  "test",
            "severity":     "High",
            "test_case_id": 1,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b"Bug created successfully" in response.data
        assert b"Linked Bug" in response.data

    def test_create_bug_stores_all_fields(self, client, app, db):
        """Created bug has correct field values in the database."""
        create_bug(client, title="DB Check Bug", module="Payments",
                   description="Payment fails", severity="Critical")
        with app.app_context():
            from app.db import get_db
            database = get_db()
            bug = database.execute(
                "SELECT * FROM bugs WHERE id = 1"
            ).fetchone()
            assert bug is not None
            assert bug["title"] == "DB Check Bug"
            assert bug["module"] == "Payments"
            assert bug["description"] == "Payment fails"
            assert bug["severity"] == "Critical"
            assert bug["status"] == "Open"

    def test_create_bug_initial_status_is_open(self, client, app, db):
        """New bug always starts with status Open."""
        create_bug(client)
        with app.app_context():
            from app.db import get_db
            database = get_db()
            bug = database.execute("SELECT status FROM bugs WHERE id = 1").fetchone()
            assert bug["status"] == "Open"
            assert bug["status"] != "In Progress"
            assert bug["status"] != "Resolved"
            assert bug["status"] != "Closed"


# ── Status Transitions ────────────────────────────────────────────────────────

class TestStatusTransitions:

    def test_open_to_in_progress(self, client):
        """Open → In Progress is valid."""
        create_bug(client)
        response = client.post("/bugs/1/update-status",
                               data={"status": "In Progress"},
                               follow_redirects=True)
        assert response.status_code == 200
        assert b"In Progress" in response.data
        assert b"Invalid transition" not in response.data

    def test_in_progress_to_resolved(self, client):
        """In Progress → Resolved is valid."""
        create_bug(client)
        client.post("/bugs/1/update-status",
                    data={"status": "In Progress"},
                    follow_redirects=True)
        response = client.post("/bugs/1/update-status",
                               data={"status": "Resolved"},
                               follow_redirects=True)
        assert response.status_code == 200
        assert b"Resolved" in response.data
        assert b"Invalid transition" not in response.data

    def test_resolved_to_closed(self, client):
        """Resolved → Closed is valid."""
        create_bug(client)
        client.post("/bugs/1/update-status",
                    data={"status": "In Progress"}, follow_redirects=True)
        client.post("/bugs/1/update-status",
                    data={"status": "Resolved"}, follow_redirects=True)
        response = client.post("/bugs/1/update-status",
                               data={"status": "Closed"},
                               follow_redirects=True)
        assert response.status_code == 200
        assert b"Closed" in response.data
        assert b"Invalid transition" not in response.data

    def test_open_to_resolved_invalid(self, client):
        """Open → Resolved is NOT allowed."""
        create_bug(client)
        response = client.post("/bugs/1/update-status",
                               data={"status": "Resolved"},
                               follow_redirects=True)
        assert response.status_code == 200
        assert b"Invalid transition" in response.data
        assert b"Resolved" not in response.data or b"Invalid transition" in response.data

    def test_open_to_closed_invalid(self, client):
        """Open → Closed is NOT allowed."""
        create_bug(client)
        response = client.post("/bugs/1/update-status",
                               data={"status": "Closed"},
                               follow_redirects=True)
        assert response.status_code == 200
        assert b"Invalid transition" in response.data
        assert b"Closed" not in response.data or b"Invalid transition" in response.data

    def test_closed_to_any_status_invalid(self, client):
        """Closed → any other status is NOT allowed."""
        create_bug(client)
        client.post("/bugs/1/update-status",
                    data={"status": "In Progress"}, follow_redirects=True)
        client.post("/bugs/1/update-status",
                    data={"status": "Resolved"}, follow_redirects=True)
        client.post("/bugs/1/update-status",
                    data={"status": "Closed"}, follow_redirects=True)

        for target in ["Open", "In Progress", "Resolved"]:
            response = client.post("/bugs/1/update-status",
                                   data={"status": target},
                                   follow_redirects=True)
            assert b"Invalid transition" in response.data, \
                f"Expected rejection of Closed → {target}"

    def test_closed_has_no_transitions(self, client):
        """Closed bug shows no further transitions."""
        create_bug(client)
        client.post("/bugs/1/update-status",
                    data={"status": "In Progress"}, follow_redirects=True)
        client.post("/bugs/1/update-status",
                    data={"status": "Resolved"}, follow_redirects=True)
        client.post("/bugs/1/update-status",
                    data={"status": "Closed"}, follow_redirects=True)
        response = client.get("/bugs/1")
        assert response.status_code == 200
        assert b"No further transitions available" in response.data

    def test_status_persists_in_db_after_transition(self, client, app, db):
        """Status change is committed to the database correctly."""
        create_bug(client)
        client.post("/bugs/1/update-status",
                    data={"status": "In Progress"}, follow_redirects=True)
        with app.app_context():
            from app.db import get_db
            database = get_db()
            bug = database.execute("SELECT status FROM bugs WHERE id = 1").fetchone()
            assert bug["status"] == "In Progress"
            assert bug["status"] != "Open"

    def test_full_workflow_persists_each_step_in_db(self, client, app, db):
        """Each status step is individually committed to the database."""
        create_bug(client)

        client.post("/bugs/1/update-status",
                    data={"status": "In Progress"}, follow_redirects=True)
        with app.app_context():
            from app.db import get_db
            assert get_db().execute(
                "SELECT status FROM bugs WHERE id=1").fetchone()["status"] == "In Progress"

        client.post("/bugs/1/update-status",
                    data={"status": "Resolved"}, follow_redirects=True)
        with app.app_context():
            from app.db import get_db
            assert get_db().execute(
                "SELECT status FROM bugs WHERE id=1").fetchone()["status"] == "Resolved"

        client.post("/bugs/1/update-status",
                    data={"status": "Closed"}, follow_redirects=True)
        with app.app_context():
            from app.db import get_db
            assert get_db().execute(
                "SELECT status FROM bugs WHERE id=1").fetchone()["status"] == "Closed"


# ── Bug Data Integrity ────────────────────────────────────────────────────────

class TestBugDataIntegrity:
    """Tests that verify actual data values, not just status codes."""

    def test_bug_list_shows_all_bugs(self, client):
        """Verify bug list displays all created bugs."""
        create_bug(client, title="Bug One", severity="High")
        create_bug(client, title="Bug Two", severity="Medium")
        create_bug(client, title="Bug Three", severity="Low")

        response = client.get("/bugs/")
        assert response.status_code == 200
        assert b"Bug One" in response.data
        assert b"Bug Two" in response.data
        assert b"Bug Three" in response.data
        assert b"High" in response.data
        assert b"Medium" in response.data
        assert b"Low" in response.data

    def test_bug_list_count_matches_created(self, client, app, db):
        """Exactly N bugs appear in the DB after N creates."""
        titles = ["Alpha Bug", "Beta Bug", "Gamma Bug"]
        for t in titles:
            create_bug(client, title=t, module="Core")
        with app.app_context():
            from app.db import get_db
            count = get_db().execute("SELECT COUNT(*) FROM bugs").fetchone()[0]
            assert count == 3

    def test_bug_view_displays_correct_details(self, client):
        """Verify bug detail page shows all information."""
        create_bug(client,
                   title="Detail Test Bug",
                   module="UI",
                   description="Button not working",
                   severity="High")

        response = client.get("/bugs/1")
        assert response.status_code == 200
        assert b"Detail Test Bug" in response.data
        assert b"UI" in response.data
        assert b"Button not working" in response.data
        assert b"High" in response.data
        assert b"Open" in response.data

    def test_bug_detail_does_not_show_wrong_data(self, client):
        """Bug detail page must not bleed data from other bugs."""
        create_bug(client, title="First Bug", module="Auth",
                   description="First desc", severity="Low")
        create_bug(client, title="Second Bug", module="Payments",
                   description="Second desc", severity="Critical")

        response = client.get("/bugs/1")
        assert b"First Bug" in response.data
        assert b"Second Bug" not in response.data
        assert b"First desc" in response.data
        assert b"Second desc" not in response.data

    def test_all_severity_levels_work(self, client):
        """Verify all severity levels can be created and are stored correctly."""
        severities = ["Low", "Medium", "High", "Critical"]
        for severity in severities:
            response = create_bug(client, title=f"Bug {severity}",
                                  module=severity, severity=severity)
            assert response.status_code == 200
            assert severity.encode() in response.data
            assert b"Bug created successfully" in response.data

    def test_severity_low_is_not_high(self, client, app, db):
        """Low severity bug must not be stored as High."""
        create_bug(client, title="Low Severity Bug", severity="Low")
        with app.app_context():
            from app.db import get_db
            bug = get_db().execute("SELECT severity FROM bugs WHERE id=1").fetchone()
            assert bug["severity"] == "Low"
            assert bug["severity"] != "High"
            assert bug["severity"] != "Critical"

    def test_status_transitions_are_sequential(self, client):
        """Verify status must follow the correct workflow."""
        create_bug(client, title="Workflow Test")

        response = client.post("/bugs/1/update-status",
                               data={"status": "In Progress"},
                               follow_redirects=True)
        assert b"In Progress" in response.data
        assert b"Invalid transition" not in response.data

        response = client.post("/bugs/1/update-status",
                               data={"status": "Resolved"},
                               follow_redirects=True)
        assert b"Resolved" in response.data
        assert b"Invalid transition" not in response.data

        response = client.post("/bugs/1/update-status",
                               data={"status": "Closed"},
                               follow_redirects=True)
        assert b"Closed" in response.data
        assert b"Invalid transition" not in response.data

    def test_skipping_in_progress_step_is_rejected(self, client):
        """Open → Resolved (skipping In Progress) must be rejected."""
        create_bug(client, title="Skip Test")
        response = client.post("/bugs/1/update-status",
                               data={"status": "Resolved"},
                               follow_redirects=True)
        assert b"Invalid transition" in response.data
        # Status must remain Open
        detail = client.get("/bugs/1")
        assert b"Open" in detail.data
        assert b"Resolved" not in detail.data

    def test_bug_title_and_module_stored_exactly(self, client, app, db):
        """Title and module are stored verbatim, not altered."""
        create_bug(client, title="Exact Title Check", module="ExactModule")
        with app.app_context():
            from app.db import get_db
            bug = get_db().execute("SELECT title, module FROM bugs WHERE id=1").fetchone()
            assert bug["title"] == "Exact Title Check"
            assert bug["module"] == "ExactModule"
            assert bug["title"] != "exact title check"  # case preserved
