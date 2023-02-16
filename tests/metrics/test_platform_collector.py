import os
from importlib import reload

from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch


class PlatformCollectorest(IsolatedAsyncioTestCase):
    async def test_use_global_namespace(self):
        from asyncworker import conf
        from asyncworker.metrics import registry

        with patch.dict(os.environ, ASYNCWORKER_METRICS_APPPREFIX="myapp"):
            reload(conf)
            reload(registry)
            pc = registry.PLATFORM_COLLECTOR

            metrics = pc.collect()
            self.assertEqual(1, len(pc.collect()))

            metric_names = [m.name for m in metrics]
            expected_metric_names = ["asyncworker_myapp_python_info"]
            self.assertEqual(expected_metric_names, metric_names)
