from asyncworker.conf import INFINITY
from asyncworker.metrics.types import Histogram, Gauge

request_duration = Histogram(
    name="asyncworker_http_request_duration",
    documentation="HTTP request duration",
    labelnames=("method", "path", "status"),
    buckets=(0.01, 0.05, 0.1, INFINITY),
)

requests_in_progress = Gauge(
    name="asyncworker_http_requests_in_progress",
    documentation="Count of HTTP requests currently in progress",
    labelnames=("method", "path"),
)
