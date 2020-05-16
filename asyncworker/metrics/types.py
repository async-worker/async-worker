from abc import ABCMeta
from functools import partial

import prometheus_client as prometheus

from asyncworker.conf import settings
from asyncworker.metrics.registry import REGISTRY, DEFAULT_METRIC_NAMESAPACE


class _BaseMetric(metaclass=ABCMeta):
    pass


class _Counter(_BaseMetric, prometheus.Counter):
    pass


class _Histogram(_BaseMetric, prometheus.Histogram):
    pass


class _Gauge(_BaseMetric, prometheus.Gauge):
    pass


Counter = partial(
    _Counter, registry=REGISTRY, namespace=DEFAULT_METRIC_NAMESAPACE
)
Histogram = partial(
    _Histogram,
    registry=REGISTRY,
    buckets=settings.METRICS_DEFAULT_HISTOGRAM_BUCKETS_IN_MS,
    namespace=DEFAULT_METRIC_NAMESAPACE,
)
Gauge = partial(_Gauge, registry=REGISTRY, namespace=DEFAULT_METRIC_NAMESAPACE)
