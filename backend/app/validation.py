"""Tiny request-body validation helpers (no external schema lib)."""
import re
from datetime import date

from flask import request

from .errors import ApiError

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def get_json():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ApiError("invalid_body", "Request body must be a JSON object", 400)
    return data


def require(data, *fields):
    missing = [f for f in fields if data.get(f) in (None, "")]
    if missing:
        raise ApiError(
            "validation_error",
            "Missing required fields",
            422,
            {"missing": missing},
        )


def valid_email(value):
    if not isinstance(value, str) or not EMAIL_RE.match(value):
        raise ApiError("validation_error", "Invalid email format", 422)
    return value.lower().strip()


def valid_password(value):
    if not isinstance(value, str) or len(value) < 8:
        raise ApiError(
            "validation_error", "Password must be at least 8 characters", 422
        )
    return value


def one_of(value, allowed, field):
    if value is not None and value not in allowed:
        raise ApiError(
            "validation_error",
            f"'{field}' must be one of {sorted(allowed)}",
            422,
        )
    return value


def parse_date(value, field="due_date"):
    if value in (None, ""):
        return None
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ApiError("validation_error", f"'{field}' must be YYYY-MM-DD", 422)


def pagination():
    try:
        page = max(1, int(request.args.get("page", 1)))
        per_page = min(100, max(1, int(request.args.get("per_page", 20))))
    except ValueError:
        raise ApiError("validation_error", "page/per_page must be integers", 422)
    return page, per_page
