from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.responses import Response

REQUEST_COUNT = Counter(
    "devforge_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)
REQUEST_LATENCY = Histogram(
    "devforge_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)
GENERATION_JOBS_TOTAL = Counter(
    "devforge_generation_jobs_total",
    "Total generation jobs created",
    ["status"],
)


def metrics_response() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
