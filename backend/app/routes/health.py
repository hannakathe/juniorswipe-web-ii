from flask import Blueprint, jsonify

from ..extensions import db

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
@health_bp.get("/api/health")
def health():
    db_ok = True
    try:
        db.session.execute(db.text("SELECT 1"))
    except Exception:  # pragma: no cover
        db_ok = False
    status = 200 if db_ok else 503
    return jsonify({"status": "ok" if db_ok else "degraded", "database": db_ok}), status
