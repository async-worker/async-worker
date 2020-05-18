import platform

from prometheus_client import CollectorRegistry
from prometheus_client.metrics_core import GaugeMetricFamily

from asyncworker.metrics.collectors.base import BaseCollector


class PlatformCollector(BaseCollector):
    """Collector for python platform information"""

    def __init__(
        self, registry: CollectorRegistry, namespace: str = ""
    ) -> None:
        info = self._info()
        system = platform.system()
        if system == "Java":
            info.update(self._java())

        if namespace:
            self.namespace = f"{namespace}_"

        self._metrics = [
            self._add_metric(
                f"{self.namespace}python_info",
                "Python platform information",
                info,
            )
        ]

        registry.register(self)

    def collect(self):
        return self._metrics

    @staticmethod
    def _add_metric(
        name: str, documentation: str, data: dict
    ) -> GaugeMetricFamily:
        labels = data.keys()
        values = [data[k] for k in labels]
        g = GaugeMetricFamily(name, documentation, labels=labels)
        g.add_metric(values, 1)
        return g

    def _info(self):
        major, minor, patchlevel = platform.python_version_tuple()
        return {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "major": major,
            "minor": minor,
            "patchlevel": patchlevel,
        }

    def _java(self):
        java_version, _, vminfo, osinfo = platform.java_ver()
        vm_name, vm_release, vm_vendor = vminfo
        return {
            "jvm_version": java_version,
            "jvm_release": vm_release,
            "jvm_vendor": vm_vendor,
            "jvm_name": vm_name,
        }
