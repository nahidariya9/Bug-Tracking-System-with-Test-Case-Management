from flask import Flask, render_template
from app.db import init_db, init_app as db_init_app
import os


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    # Default configuration
    app.config["SECRET_KEY"] = "sqa-project-key"
    app.config["DATABASE"] = os.path.join(app.instance_path, "bug_tracker.db")
    
    # Load test config if passed
    if test_config:
        app.config.update(test_config)
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    db_init_app(app)

    with app.app_context():
        init_db()

    # Register blueprints
    from app.routes.bugs import bp as bugs_bp
    from app.routes.test_cases import bp as tc_bp
    from app.routes.executions import bp as exec_bp
    from app.routes.reports import bp as reports_bp
    app.register_blueprint(bugs_bp)
    app.register_blueprint(tc_bp)
    app.register_blueprint(exec_bp)
    app.register_blueprint(reports_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app