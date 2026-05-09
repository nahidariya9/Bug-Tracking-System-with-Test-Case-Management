from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db import get_db

bp = Blueprint("executions", __name__, url_prefix="/executions")


@bp.route("/")
def list_executions():
    db         = get_db()
    executions = db.execute("""
        SELECT e.*, tc.title AS tc_title
        FROM test_executions e
        JOIN test_cases tc ON e.test_case_id = tc.id
        ORDER BY e.executed_at DESC
    """).fetchall()
    return render_template("executions/list.html", executions=executions)


@bp.route("/run", methods=["GET", "POST"])
def run_execution():
    db    = get_db()
    cases = db.execute(
        "SELECT id, title FROM test_cases ORDER BY title"
    ).fetchall()

    if request.method == "POST":
        test_case_id = request.form.get("test_case_id", type=int)
        result       = request.form["result"]
        notes        = request.form["notes"].strip()

        errors = []
        if not test_case_id:
            errors.append("Please select a test case.")
        if result not in ("Pass", "Fail"):
            errors.append("Result must be Pass or Fail.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("executions/run.html", cases=cases)

        db.execute("""
            INSERT INTO test_executions (test_case_id, result, notes)
            VALUES (?, ?, ?)
        """, (test_case_id, result, notes))
        db.commit()
        flash(f"Execution recorded: {result}.", "success")
        return redirect(url_for("executions.list_executions"))

    return render_template("executions/run.html", cases=cases)


@bp.route("/<int:exec_id>")
def view_execution(exec_id):
    db        = get_db()
    execution = db.execute("""
        SELECT e.*, tc.title AS tc_title, tc.expected AS tc_expected
        FROM test_executions e
        JOIN test_cases tc ON e.test_case_id = tc.id
        WHERE e.id = ?
    """, (exec_id,)).fetchone()

    if execution is None:
        flash("Execution not found.", "danger")
        return redirect(url_for("executions.list_executions"))

    return render_template("executions/view.html", execution=execution)