import prometheus_client as prometheus
from prometheus_client.platform_collector import PlatformCollector
from prometheus_client.process_collector import ProcessCollector

from asyncworker.conf import settings

NAMESPACE = (
    f"{settings.METRICS_NAMESPACE}_{settings.METRICS_APPPREFIX}"
    if settings.METRICS_APPPREFIX
    else f"{settings.METRICS_NAMESPACE}"
)

REGISTRY = prometheus.CollectorRegistry(auto_describe=True)
generate_latest = prometheus.generate_latest

PLATFORM_COLLECTOR = PlatformCollector(registry=REGISTRY)
PROCESS_COLLECTOR = ProcessCollector(namespace=NAMESPACE, registry=REGISTRY)
