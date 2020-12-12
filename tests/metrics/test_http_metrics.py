import asyncio
from http import HTTPStatus

from aiohttp import ClientSession
from aiohttp.web_exceptions import HTTPNotFound
from aiohttp.web_response import Response
from asynctest import TestCase, patch, CoroutineMock

from asyncworker import App, RouteTypes
from asyncworker.conf import settings


class HTTPMetricsTests(TestCase):
    async def setUp(self):
        self.app = App()
        self.client = ClientSession()

        self.callback = callback = CoroutineMock()
        self.route_path = "/mock_handler"
        self.route_method = "GET"
        self.metrics = metrics = patch(
            "asyncworker.metrics.aiohttp_resources.metrics"
        ).start()

        @self.app.http._route(
            routes=[self.route_path], method=self.route_method
        )
        async def handler(request):
            metrics.requests_in_progress.labels.assert_called_once_with(
                method=request.method, path=request.path
            )
            metrics.requests_in_progress.labels.return_value.inc.assert_called_once()
            metrics.requests_in_progress.labels.return_value.dec.assert_not_called()
            await callback(request)
            return Response(text="ok")

        await self.app.startup()

    async def tearDown(self):
        await asyncio.gather(self.app.shutdown(), self.client.close())
        patch.stopall()

    async def test_successful_request(self):
        url = (
            f"http://{settings.HTTP_HOST}:{settings.HTTP_PORT}{self.route_path}"
        )

        async with self.client.get(url) as response:
            content = await response.text()
            self.assertEqual(response.status, HTTPStatus.OK)

        self.metrics.response_size.labels.assert_called_once_with(
            method=self.route_method, path=self.route_path
        )
        self.metrics.request_duration.labels.assert_called_once_with(
            method=self.route_method,
            path=self.route_path,
            status=response.status,
        )
        self.metrics.requests_in_progress.labels.assert_called_with(
            method=self.route_method, path=self.route_path
        )
        self.metrics.response_size.labels.return_value.observe.assert_called_once_with(
            len(content)
        )
        self.metrics.request_duration.labels.return_value.observe.assert_called_once()
        self.metrics.requests_in_progress.labels.return_value.dec.assert_called_once()

    async def test_unsuccessful_request(self):
        url = (
            f"http://{settings.HTTP_HOST}:{settings.HTTP_PORT}{self.route_path}"
        )
        self.callback.side_effect = KeyError
        async with self.client.get(url) as response:
            await response.text()
            self.assertEqual(response.status, HTTPStatus.INTERNAL_SERVER_ERROR)

        self.metrics.response_size.labels.assert_not_called()
        self.metrics.request_duration.labels.assert_called_once_with(
            method=self.route_method,
            path=self.route_path,
            status=response.status,
        )
        self.metrics.requests_in_progress.labels.assert_called_with(
            method=self.route_method, path=self.route_path
        )
        self.metrics.response_size.labels.return_value.observe.assert_not_called()
        self.metrics.request_duration.labels.return_value.observe.assert_called_once()
        self.metrics.requests_in_progress.labels.return_value.dec.assert_called_once()

    async def test_notfound_request(self):
        url = (
            f"http://{settings.HTTP_HOST}:{settings.HTTP_PORT}{self.route_path}"
        )
        self.callback.side_effect = HTTPNotFound
        async with self.client.get(url) as response:
            content = await response.text()
            self.assertEqual(response.status, HTTPStatus.NOT_FOUND)

        self.metrics.response_size.labels.assert_called_once_with(
            method=self.route_method, path=self.route_path
        )
        self.metrics.request_duration.labels.assert_called_once_with(
            method=self.route_method,
            path=self.route_path,
            status=response.status,
        )
        self.metrics.requests_in_progress.labels.assert_called_with(
            method=self.route_method, path=self.route_path
        )
        self.metrics.response_size.labels.return_value.observe.assert_called_once_with(
            len(content)
        )
        self.metrics.request_duration.labels.return_value.observe.assert_called_once()
        self.metrics.requests_in_progress.labels.return_value.dec.assert_called_once()
