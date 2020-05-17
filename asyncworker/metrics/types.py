from abc import ABCMeta
from functools import partial

import prometheus_client as prometheus

from asyncworker.conf import settings
from asyncworker.metrics.registry import REGISTRY


class _BaseMetric(metaclass=ABCMeta):
    pass


class Counter(_BaseMetric, prometheus.Counter):
    def __init__(self, name, documentation, **kwargs) -> None:
        kwargs["namespace"] = settings.METRICS_NAMESPACE
        kwargs["registry"] = REGISTRY
        super().__init__(name, documentation, **kwargs)


class Histogram(_BaseMetric, prometheus.Histogram):
    def __init__(self, name, documentation, **kwargs) -> None:
        kwargs["namespace"] = settings.METRICS_NAMESPACE
        kwargs["registry"] = REGISTRY
        kwargs["buckets"] = settings.METRICS_DEFAULT_HISTOGRAM_BUCKETS_IN_MS
        super().__init__(name, documentation, **kwargs)


class Gauge(_BaseMetric, prometheus.Gauge):
    def __init__(self, name, documentation, **kwargs) -> None:
        kwargs["namespace"] = settings.METRICS_NAMESPACE
        kwargs["registry"] = REGISTRY
        super().__init__(name, documentation, **kwargs)
