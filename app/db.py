import sqlite3
from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()

    db.executescript("""
        CREATE TABLE IF NOT EXISTS test_cases (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT    NOT NULL,
            description TEXT,
            expected    TEXT    NOT NULL,
            created_at  TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS bugs (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            title        TEXT    NOT NULL,
            module       TEXT,
            description  TEXT,
            severity     TEXT    NOT NULL CHECK(severity IN ('Low','Medium','High','Critical')),
            status       TEXT    NOT NULL DEFAULT 'Open'
                                          CHECK(status IN ('Open','In Progress','Resolved','Closed')),
            test_case_id INTEGER,
            created_at   TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (test_case_id) REFERENCES test_cases(id)
        );

        CREATE TABLE IF NOT EXISTS test_executions (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            test_case_id INTEGER NOT NULL,
            result       TEXT    NOT NULL CHECK(result IN ('Pass','Fail')),
            notes        TEXT,
            executed_at  TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (test_case_id) REFERENCES test_cases(id)
        );
    """)
    db.commit()


def init_app(app):
    app.teardown_appcontext(close_db)