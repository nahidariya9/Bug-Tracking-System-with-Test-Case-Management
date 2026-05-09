from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db import get_db

bp = Blueprint("bugs", __name__, url_prefix="/bugs")

# Valid status transitions
TRANSITIONS = {
    "Open":        ["In Progress"],
    "In Progress": ["Resolved"],
    "Resolved":    ["Closed", "In Progress"],
    "Closed":      []
}

SEVERITIES = ["Low", "Medium", "High", "Critical"]
STATUSES   = ["Open", "In Progress", "Resolved", "Closed"]


@bp.route("/")
def list_bugs():
    db   = get_db()
    bugs = db.execute("""
        SELECT b.*, tc.title AS tc_title
        FROM bugs b
        LEFT JOIN test_cases tc ON b.test_case_id = tc.id
        ORDER BY b.created_at DESC
    """).fetchall()
    return render_template("bugs/list.html", bugs=bugs)


@bp.route("/create", methods=["GET", "POST"])
def create_bug():
    db           = get_db()
    test_case_id = request.args.get("test_case_id", type=int)
    tc           = None
    if test_case_id:
        tc = db.execute(
            "SELECT * FROM test_cases WHERE id = ?", (test_case_id,)
        ).fetchone()

    if request.method == "POST":
        title        = request.form["title"].strip()
        module       = request.form.get("module", "").strip()
        description  = request.form["description"].strip()
        severity     = request.form["severity"]
        test_case_id = request.form.get("XXtest_case_idXX", type=int)

        # --- Validation ---
        errors = []
        if not title:
            errors.append("Title is required.")
        if severity not in SEVERITIES:
            errors.append("Invalid severity.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("bugs/create.html",
                                   severities=SEVERITIES,
                                   tc=tc,
                                   test_case_id=test_case_id)

        # --- Duplicate check (same title + module) ---
        duplicate = db.execute(
            "SELECT id FROM bugs WHERE title = ? AND module = ?",
            (title, module)
        ).fetchone()
        if duplicate:
            flash(
                f"A bug with this title and module already exists "
                f"(Bug #{duplicate['id']}).",
                "danger"
            )
            return render_template("bugs/create.html",
                                   severities=SEVERITIES,
                                   tc=tc,
                                   test_case_id=test_case_id)

        # --- Insert ---
        db.execute("""
            INSERT INTO bugs (title, module, description, severity, status, test_case_id)
            VALUES (?, ?, ?, ?, 'Open', ?)
        """, (title, module, description, severity, test_case_id))
        db.commit()
        flash("Bug created successfully.", "success")
        return redirect(url_for("bugs.list_bugs"))

    return render_template("bugs/create.html",
                           severities=SEVERITIES,
                           tc=tc,
                           test_case_id=test_case_id)


@bp.route("/<int:bug_id>")
def view_bug(bug_id):
    db  = get_db()
    bug = db.execute("""
        SELECT b.*, tc.title AS tc_title
        FROM bugs b
        LEFT JOIN test_cases tc ON b.test_case_id = tc.id
        WHERE b.id = ?
    """, (bug_id,)).fetchone()

    if bug is None:
        flash("Bug not found.", "danger")
        return redirect(url_for("bugs.list_bugs"))

    allowed = TRANSITIONS.get(bug["status"], [])
    return render_template("bugs/view.html",
                           bug=bug,
                           allowed=allowed,
                           statuses=STATUSES)


@bp.route("/<int:bug_id>/update-status", methods=["POST"])
def update_status(bug_id):
    db         = get_db()
    new_status = request.form["status"]
    bug        = db.execute(
        "SELECT * FROM bugs WHERE id = ?", (bug_id,)
    ).fetchone()

    if bug is None:
        flash("Bug not found.", "danger")
        return redirect(url_for("bugs.list_bugs"))

    allowed = TRANSITIONS.get(bug["status"], [])
    if new_status not in allowed:
        flash(
            f"Invalid transition: '{bug['status']}' → '{new_status}'.",
            "danger"
        )
        return redirect(url_for("bugs.view_bug", bug_id=bug_id))

    db.execute(
        "UPDATE bugs SET status = ? WHERE id = ?", (new_status, bug_id)
    )
    db.commit()
    flash(f"Status updated to '{new_status}'.", "success")
    return redirect(url_for("bugs.view_bug", bug_id=bug_id))


@bp.route("/<int:bug_id>/edit", methods=["GET", "POST"])
def edit_bug(bug_id):
    db = get_db()
    bug = db.execute("SELECT * FROM bugs WHERE id = ?", (bug_id,)).fetchone()
    
    if bug is None:
        flash("Bug not found.", "danger")
        return redirect(url_for("bugs.list_bugs"))
    
    if request.method == "POST":
        title        = request.form["title"].strip()
        module       = request.form.get("module", "").strip()
        description  = request.form["description"].strip()
        severity     = request.form["severity"]
        test_case_id = request.form.get("test_case_id", type=int) or None
        
        # Validation
        errors = []
        if not title:
            errors.append("Title is required.")
        if severity not in SEVERITIES:
            errors.append("Invalid severity.")
        
        if errors:
            for e in errors:
                flash(e, "danger")
            test_cases = db.execute("SELECT id, title FROM test_cases ORDER BY title").fetchall()
            return render_template("bugs/edit.html",
                                   bug=bug,
                                   severities=SEVERITIES,
                                   test_cases=test_cases)
        
        # Update bug
        db.execute("""
            UPDATE bugs 
            SET title = ?, module = ?, description = ?, severity = ?, test_case_id = ?
            WHERE id = ?
        """, (title, module, description, severity, test_case_id, bug_id))
        db.commit()
        flash("Bug updated successfully.", "success")
        return redirect(url_for("bugs.view_bug", bug_id=bug_id))
    
    # GET request - show form
    test_cases = db.execute("SELECT id, title FROM test_cases ORDER BY title").fetchall()
    return render_template("bugs/edit.html",
                           bug=bug,
                           severities=SEVERITIES,
                           test_cases=test_cases)


@bp.route("/<int:bug_id>/delete", methods=["POST"])
def delete_bug(bug_id):
    db = get_db()
    bug = db.execute("SELECT * FROM bugs WHERE id = ?", (bug_id,)).fetchone()
    
    if bug is None:
        flash("Bug not found.", "danger")
        return redirect(url_for("bugs.list_bugs"))
    
    db.execute("DELETE FROM bugs WHERE id = ?", (bug_id,))
    db.commit()
    flash(f"Bug #{bug_id} deleted successfully.", "success")
    return redirect(url_for("bugs.list_bugs"))