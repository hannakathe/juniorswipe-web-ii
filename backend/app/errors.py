"""Uniform JSON error handling."""
from flask import jsonify
from werkzeug.exceptions import HTTPException


class ApiError(Exception):
    def __init__(self, code: str, message: str, status: int = 400, details=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status
        self.details = details or {}

    def to_response(self):
        body = {"error": {"code": self.code, "message": self.message}}
        if self.details:
            body["error"]["details"] = self.details
        return jsonify(body), self.status


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def _handle_api_error(err: ApiError):
        return err.to_response()

    @app.errorhandler(HTTPException)
    def _handle_http(err: HTTPException):
        return (
            jsonify({"error": {"code": err.name.lower().replace(" ", "_"),
                               "message": err.description}}),
            err.code,
        )

    @app.errorhandler(Exception)
    def _handle_unexpected(err: Exception):  # pragma: no cover - safety net
        app.logger.exception("Unhandled error")
        return (
            jsonify({"error": {"code": "internal_error",
                               "message": "Unexpected server error"}}),
            500,
        )
