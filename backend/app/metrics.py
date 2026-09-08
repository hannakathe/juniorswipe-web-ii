"""Prometheus metrics: request counter, latency histogram, /metrics endpoint."""
import time

from flask import Blueprint, Response, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
)
REQUEST_ERRORS = Counter(
    "http_request_errors_total",
    "HTTP responses with status >= 400",
    ["method", "endpoint", "status"],
)

metrics_bp = Blueprint("metrics", __name__)


@metrics_bp.get("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


def init_metrics(app):
    @app.before_request
    def _start_timer():
        request._start_time = time.perf_counter()

    @app.after_request
    def _record(response):
        endpoint = request.endpoint or "unknown"
        if endpoint == "metrics.metrics":
            return response
        elapsed = time.perf_counter() - getattr(request, "_start_time", time.perf_counter())
        labels = (request.method, endpoint)
        REQUEST_LATENCY.labels(*labels).observe(elapsed)
        REQUEST_COUNT.labels(request.method, endpoint, response.status_code).inc()
        if response.status_code >= 400:
            REQUEST_ERRORS.labels(request.method, endpoint, response.status_code).inc()
        return response

    app.register_blueprint(metrics_bp)
