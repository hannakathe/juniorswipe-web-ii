"""Application factory."""
import os

from flask import Flask, jsonify
from flask_cors import CORS

from .config import get_config
from .errors import register_error_handlers
from .extensions import db
from .metrics import init_metrics


def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    db.init_app(app)
    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )

    os.makedirs(app.config["STORAGE_DIR"], exist_ok=True)

    from .routes import ALL_BLUEPRINTS
    from . import models  # noqa: F401  (register models with SQLAlchemy)

    for bp in ALL_BLUEPRINTS:
        app.register_blueprint(bp)

    register_error_handlers(app)
    init_metrics(app)

    @app.get("/")
    def index():
        return jsonify({
            "service": "juniorswipe-api",
            "status": "running",
            "docs": "/api/health, /metrics, /api/auth/*, /api/projects, /api/tasks",
        })

    with app.app_context():
        db.create_all()
        if app.config.get("SEED_ON_STARTUP"):
            from .seed import seed
            seed(app)

    return app
