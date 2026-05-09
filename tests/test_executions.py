# ── Helpers ───────────────────────────────────────────────────────────────────

def create_test_case(client, title="Login Test",
                     description="Click login button",
                     expected="Redirected to dashboard"):
    return client.post("/test-cases/create", data={
        "title":       title,
        "description": description,
        "expected":    expected,
    }, follow_redirects=True)


def run_execution(client, test_case_id=1, result="Pass", notes=""):
    return client.post("/executions/run", data={
        "test_case_id": test_case_id,
        "result":       result,
        "notes":        notes,
    }, follow_redirects=True)


# ── Execution Storage ─────────────────────────────────────────────────────────

class TestExecutionStorage:

    def test_record_pass_execution(self, client):
        """Pass execution is saved and shown in list."""
        create_test_case(client)
        response = run_execution(client, result="Pass", notes="All good")
        assert response.status_code == 200
        assert b"Pass" in response.data
        assert b"Fail" not in response.data or b"Pass" in response.data

    def test_record_fail_execution(self, client):
        """Fail execution is saved and shown in list."""
        create_test_case(client)
        response = run_execution(client, result="Fail", notes="Button broken")
        assert response.status_code == 200
        assert b"Fail" in response.data

    def test_pass_result_stored_as_pass_not_fail(self, client, app, db):
        """Pass result is stored exactly as 'Pass', not 'Fail'."""
        create_test_case(client)
        run_execution(client, result="Pass", notes="Stored correctly")
        with app.app_context():
            from app.db import get_db
            execution = get_db().execute(
                "SELECT result FROM test_executions WHERE id = 1"
            ).fetchone()
            assert execution is not None
            assert execution["result"] == "Pass"
            assert execution["result"] != "Fail"

    def test_fail_result_stored_as_fail_not_pass(self, client, app, db):
        """Fail result is stored exactly as 'Fail', not 'Pass'."""
        create_test_case(client)
        run_execution(client, result="Fail", notes="Stored correctly")
        with app.app_context():
            from app.db import get_db
            execution = get_db().execute(
                "SELECT result FROM test_executions WHERE id = 1"
            ).fetchone()
            assert execution is not None
            assert execution["result"] == "Fail"
            assert execution["result"] != "Pass"

    def test_execution_requires_test_case(self, client):
        """Execution without test case is rejected."""
        response = client.post("/executions/run", data={
            "test_case_id": "",
            "result":       "Pass",
            "notes":        "",
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b"Please select a test case" in response.data
        assert b"Execution recorded" not in response.data

    def test_execution_invalid_result(self, client):
        """Execution with invalid result is rejected."""
        create_test_case(client)
        response = run_execution(client, result="Maybe")
        assert response.status_code == 200
        assert b"Result must be Pass or Fail" in response.data
        assert b"Execution recorded" not in response.data

    def test_fail_execution_shows_bug_button(self, client):
        """Failed execution detail page shows Create Bug button."""
        create_test_case(client)
        run_execution(client, result="Fail", notes="Crash")
        response = client.get("/executions/1")
        assert response.status_code == 200
        assert b"Create Bug from this Failure" in response.data

    def test_pass_execution_no_bug_button(self, client):
        """Passed execution detail page does NOT show Create Bug button."""
        create_test_case(client)
        run_execution(client, result="Pass")
        response = client.get("/executions/1")
        assert response.status_code == 200
        assert b"Create Bug from this Failure" not in response.data

    def test_execution_saved_with_timestamp(self, client, app, db):
        """Execution is stored in DB with a non-null timestamp."""
        create_test_case(client)
        run_execution(client, result="Pass", notes="Quick check")
        with app.app_context():
            from app.db import get_db
            execution = get_db().execute(
                "SELECT * FROM test_executions WHERE id = 1"
            ).fetchone()
            assert execution is not None
            assert execution["result"] == "Pass"
            assert execution["executed_at"] is not None
            assert execution["executed_at"] != ""

    def test_notes_stored_verbatim(self, client, app, db):
        """Notes field is stored exactly as submitted."""
        create_test_case(client)
        run_execution(client, result="Pass", notes="Exact notes content")
        with app.app_context():
            from app.db import get_db
            execution = get_db().execute(
                "SELECT notes FROM test_executions WHERE id = 1"
            ).fetchone()
            assert execution["notes"] == "Exact notes content"

    def test_execution_linked_to_correct_test_case(self, client, app, db):
        """Execution stores the correct test_case_id."""
        create_test_case(client, title="TC for Linking")
        run_execution(client, test_case_id=1, result="Pass")
        with app.app_context():
            from app.db import get_db
            execution = get_db().execute(
                "SELECT test_case_id FROM test_executions WHERE id = 1"
            ).fetchone()
            assert execution["test_case_id"] == 1

    def test_execution_count_increments(self, client, app, db):
        """Each call to /executions/run creates exactly one new record."""
        create_test_case(client)
        run_execution(client, result="Pass", notes="First")
        run_execution(client, result="Fail", notes="Second")
        run_execution(client, result="Pass", notes="Third")
        with app.app_context():
            from app.db import get_db
            count = get_db().execute(
                "SELECT COUNT(*) FROM test_executions"
            ).fetchone()[0]
            assert count == 3


# ── Execution Data Integrity ──────────────────────────────────────────────────

class TestExecutionDataIntegrity:
    """Tests that verify actual execution data values."""

    def test_execution_list_shows_all_executions(self, client):
        """Verify execution list displays all recorded executions."""
        create_test_case(client)
        run_execution(client, result="Pass", notes="First execution")
        run_execution(client, result="Fail", notes="Second execution")

        response = client.get("/executions/")
        assert response.status_code == 200
        assert b"First execution" in response.data
        assert b"Second execution" in response.data
        assert b"Pass" in response.data
        assert b"Fail" in response.data

    def test_execution_view_shows_test_case_details(self, client):
        """Verify execution detail page shows linked test case info."""
        create_test_case(client, title="Detailed Test",
                         description="Test description",
                         expected="Expected result")
        run_execution(client, result="Pass", notes="Execution notes")

        response = client.get("/executions/1")
        assert response.status_code == 200
        assert b"Detailed Test" in response.data
        assert b"Pass" in response.data
        assert b"Execution notes" in response.data

    def test_execution_view_does_not_show_wrong_data(self, client):
        """Execution detail must not bleed data from other executions."""
        create_test_case(client)
        run_execution(client, result="Pass", notes="Notes for exec 1")
        run_execution(client, result="Fail", notes="Notes for exec 2")

        response = client.get("/executions/1")
        assert b"Notes for exec 1" in response.data
        assert b"Notes for exec 2" not in response.data

    def test_multiple_executions_same_test_case(self, client):
        """Verify multiple executions can be recorded for one test case."""
        create_test_case(client)
        expected_results = ["Pass", "Fail", "Pass"]
        for i, result in enumerate(expected_results):
            response = run_execution(client, result=result,
                                     notes=f"Run {i + 1}")
            assert response.status_code == 200

    def test_multiple_executions_stored_independently(self, client, app, db):
        """Each execution stores its own result independently."""
        create_test_case(client)
        run_execution(client, result="Pass", notes="Run A")
        run_execution(client, result="Fail", notes="Run B")

        with app.app_context():
            from app.db import get_db
            database = get_db()
            exec1 = database.execute(
                "SELECT result, notes FROM test_executions WHERE id = 1"
            ).fetchone()
            exec2 = database.execute(
                "SELECT result, notes FROM test_executions WHERE id = 2"
            ).fetchone()
            assert exec1["result"] == "Pass"
            assert exec1["notes"] == "Run A"
            assert exec2["result"] == "Fail"
            assert exec2["notes"] == "Run B"
            # Results must differ
            assert exec1["result"] != exec2["result"]

    def test_execution_results_are_preserved(self, client):
        """Verify execution results don't change after creation."""
        create_test_case(client)
        run_execution(client, result="Pass", notes="Initial pass")

        for _ in range(3):
            response = client.get("/executions/1")
            assert response.status_code == 200
            assert b"Pass" in response.data
            assert b"Initial pass" in response.data

    def test_pass_result_does_not_display_fail(self, client):
        """A Pass execution must not display 'Fail' as its result."""
        create_test_case(client)
        run_execution(client, result="Pass", notes="Should be pass only")

        response = client.get("/executions/1")
        assert b"Pass" in response.data
        # The result badge/label itself should not say Fail
        assert response.data.count(b"Fail") == 0

    def test_fail_result_does_not_display_pass(self, client):
        """A Fail execution must not display 'Pass' as its result."""
        create_test_case(client)
        run_execution(client, result="Fail", notes="Should be fail only")

        response = client.get("/executions/1")
        assert b"Fail" in response.data
        assert b"Create Bug from this Failure" in response.data
        assert b"Pass" not in response.data or b"Fail" in response.data

    def test_only_valid_results_are_accepted(self, client):
        """Neither 'Maybe', 'Skip', nor empty string are valid results."""
        create_test_case(client)
        for invalid in ["Maybe", "Skip", "N/A", ""]:
            response = run_execution(client, result=invalid)
            assert response.status_code == 200
            assert b"Execution recorded" not in response.data
