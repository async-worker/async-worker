from functools import partial
from http import HTTPStatus

from aiohttp import web
from asynctest import TestCase
from prometheus_client.parser import text_string_to_metric_families

from asyncworker import App, RouteTypes
from asyncworker.conf import settings
from asyncworker.http.decorators import parse_path
from asyncworker.metrics import Counter, Gauge, Histogram
from asyncworker.metrics.aiohttp_resources import metrics_route_handler
from asyncworker.metrics.registry import REGISTRY, DEFAULT_METRIC_NAMESAPACE
from asyncworker.testing import HttpClientContext


class MetricsEndpointTest(TestCase):
    use_default_loop = True
    maxDiff = None

    async def setUp(self):
        self.app = App()
        self.app.route(["/metrics"], type=RouteTypes.HTTP, methods=["GET"])(
            metrics_route_handler
        )

    async def test_count_metric(self):
        metric_name = "myapp_example_counter"
        counter = Counter(metric_name, "Um contador simples", registry=REGISTRY)

        @self.app.route(["/foo"], type=RouteTypes.HTTP, methods=["GET"])
        async def _handler():
            counter.inc()
            return web.json_response({})

        async with HttpClientContext(self.app) as client:
            await client.get("/foo")
            await client.get("/foo")

            metrics = await client.get("/metrics")
            self.assertEqual(HTTPStatus.OK, metrics.status)

            data = await metrics.text()
            metrics_parsed = list(text_string_to_metric_families(data))
            count_metric = [
                m
                for m in metrics_parsed
                if m.name == f"{DEFAULT_METRIC_NAMESAPACE}_{metric_name}"
            ]
            self.assertEqual(1, len(count_metric))
            self.assertEqual(2.0, count_metric[0].samples[0].value)

    async def test_gauge_metric(self):
        metric_name = "myapp_example_gauge"
        gauge = Gauge(metric_name, "um Gauge simples", registry=REGISTRY)

        @self.app.route(["/foo/{value}"], type=RouteTypes.HTTP, methods=["GET"])
        @parse_path
        async def _handler(value: int):
            gauge.inc(value)
            return web.json_response({})

        async with HttpClientContext(self.app) as client:
            await client.get("/foo/10")
            await client.get("/foo/20")
            await client.get("/foo/-5")

            metrics = await client.get("/metrics")
            self.assertEqual(HTTPStatus.OK, metrics.status)

            data = await metrics.text()
            metrics_parsed = list(text_string_to_metric_families(data))
            gauge_metric = [
                m
                for m in metrics_parsed
                if m.name == f"{DEFAULT_METRIC_NAMESAPACE}_{metric_name}"
            ]
            self.assertEqual(1, len(gauge_metric))
            self.assertEqual(25.0, gauge_metric[0].samples[0].value)

    async def test_histogram_metric(self):
        metric_name = "myapp_example_histogram"
        histogram = Histogram(
            metric_name, "um Histogram simples", registry=REGISTRY
        )

        @self.app.route(["/foo/{value}"], type=RouteTypes.HTTP, methods=["GET"])
        @parse_path
        async def _handler(value: int):
            histogram.observe(value)
            return web.json_response({})

        async with HttpClientContext(self.app) as client:
            await client.get("/foo/8")
            await client.get("/foo/20")
            await client.get("/foo/12")
            await client.get("/foo/201")

            metrics = await client.get("/metrics")
            self.assertEqual(HTTPStatus.OK, metrics.status)

            data = await metrics.text()
            metrics_parsed = list(text_string_to_metric_families(data))
            histogram_metric = [
                m
                for m in metrics_parsed
                if m.name == f"{DEFAULT_METRIC_NAMESAPACE}_{metric_name}"
            ]
            self.assertEqual(1, len(histogram_metric))
            self._assert_bucket_value(
                1.0,
                settings.METRICS_DEFAULT_HISTOGRAM_BUCKETS_IN_MS[0],
                histogram_metric[0].samples[0],
            )
            self._assert_bucket_value(
                3.0,
                settings.METRICS_DEFAULT_HISTOGRAM_BUCKETS_IN_MS[1],
                histogram_metric[0].samples[1],
            )
            self._assert_bucket_value(
                3.0,
                settings.METRICS_DEFAULT_HISTOGRAM_BUCKETS_IN_MS[3],
                histogram_metric[0].samples[3],
            )

    def _assert_bucket_value(self, expected_value, bucket_value, metric):
        self.assertEqual(
            {"value": expected_value, "le": str(float(bucket_value))},
            {"value": metric.value, **metric.labels},
        )
