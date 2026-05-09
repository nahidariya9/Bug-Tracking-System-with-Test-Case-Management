from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db import get_db

bp = Blueprint("test_cases", __name__, url_prefix="/test-cases")


@bp.route("/")
def list_test_cases():
    db    = get_db()
    cases = db.execute(
        "SELECT * FROM test_cases ORDER BY created_at DESC"
    ).fetchall()
    return render_template("test_cases/list.html", cases=cases)


@bp.route("/create", methods=["GET", "POST"])
def create_test_case():
    if request.method == "POST":
        title       = request.form["title"].strip()
        description = request.form["description"].strip()
        expected    = request.form["expected"].strip()

        errors = []
        if not title:
            errors.append("Title is required.")
        if not expected:
            errors.append("Expected result is required.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("test_cases/create.html")

        db = get_db()
        db.execute(
            "INSERT INTO test_cases (title, description, expected) VALUES (?, ?, ?)",
            (title, description, expected)
        )
        db.commit()
        flash("Test case created successfully.", "success")
        return redirect(url_for("test_cases.list_test_cases"))

    return render_template("test_cases/create.html")


@bp.route("/<int:tc_id>")
def view_test_case(tc_id):
    db = get_db()

    # Get test case
    tc = db.execute(
        "SELECT * FROM test_cases WHERE id = ?", (tc_id,)
    ).fetchone()

    if tc is None:
        flash("Test case not found.", "danger")
        return redirect(url_for("test_cases.list_test_cases"))

    # Get all bugs linked to this test case
    bugs = db.execute(
        "SELECT * FROM bugs WHERE test_case_id = ? ORDER BY created_at DESC",
        (tc_id,)
    ).fetchall()

    # Get all executions for this test case
    executions = db.execute("""
        SELECT * FROM test_executions
        WHERE test_case_id = ?
        ORDER BY executed_at DESC
    """, (tc_id,)).fetchall()

    return render_template("test_cases/view.html",
                           tc=tc,
                           bugs=bugs,
                           executions=executions)