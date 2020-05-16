import prometheus_client as prometheus
from prometheus_client.platform_collector import PlatformCollector
from prometheus_client.process_collector import ProcessCollector

DEFAULT_METRIC_NAMESAPACE = "asyncworker"

REGISTRY = prometheus.CollectorRegistry(auto_describe=True)
generate_latest = prometheus.generate_latest

PLATFORM_COLLECTOR = PlatformCollector(registry=REGISTRY)
PROCESS_COLLECTOR = ProcessCollector(
    namespace=DEFAULT_METRIC_NAMESAPACE, registry=REGISTRY
)
