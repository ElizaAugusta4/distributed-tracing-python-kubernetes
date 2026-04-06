import time
from typing import Iterable

from flask import Response, g, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

HTTP_REQUESTS_TOTAL = Counter(
    "http_server_requests_total",
    "Total HTTP requests.",
    ["service", "method", "path", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_server_request_duration_seconds",
    "HTTP request latency in seconds.",
    ["service", "method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)


def _normalized_path_label() -> str:
    rule = getattr(getattr(request, "url_rule", None), "rule", None)
    if isinstance(rule, str) and rule:
        return rule
    return "unknown"


def setup_metrics(app, service_name: str, exclude_paths: Iterable[str] = ("/metrics", "/healthz", "/readyz")):
    excluded = set(exclude_paths)

    @app.before_request
    def _metrics_before_request():
        if request.path in excluded:
            return None
        g._metrics_start_time = time.monotonic()
        return None

    @app.after_request
    def _metrics_after_request(response):
        if request.path in excluded:
            return response

        path_label = _normalized_path_label()

        start = getattr(g, "_metrics_start_time", None)
        if start is not None:
            duration = max(0.0, time.monotonic() - start)
            HTTP_REQUEST_DURATION_SECONDS.labels(
                service=service_name,
                method=request.method,
                path=path_label,
            ).observe(duration)

        HTTP_REQUESTS_TOTAL.labels(
            service=service_name,
            method=request.method,
            path=path_label,
            status_code=str(response.status_code),
        ).inc()
        return response

    if "metrics" not in app.view_functions:

        @app.get("/metrics")
        def metrics():
            return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

    return app
