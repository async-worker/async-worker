from asyncworker.conf import INFINITY
from asyncworker.metrics.types import Histogram, Gauge, exponential_buckets

request_duration = Histogram(
    name="http_request_duration",
    documentation="HTTP request duration",
    labelnames=("method", "path", "status"),
    buckets=(0.01, 0.05, 0.1, INFINITY),
)

requests_in_progress = Gauge(
    name="http_requests_in_progress",
    documentation="Count of HTTP requests currently in progress",
    labelnames=("method", "path"),
)

response_size = Histogram(
    name="http_response_size_bytes",
    documentation="HTTP response size in bytes",
    labelnames=("method", "path"),
    buckets=exponential_buckets(start=100, factor=10, count=5),
)
