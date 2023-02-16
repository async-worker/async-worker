from unittest.mock import patch, AsyncMock

import aioamqp

from asyncworker.easyqueue.queue import JsonQueue, QueueConsumerDelegate


class AsyncBaseTestCase:
    test_queue_name = "test_queue"
    consumer_tag = "consumer_666"

    def setUp(self):
        self.conn_params = dict(
            host="money.que.é.good",
            username="nós",
            password="não",
            virtual_host="have",
            heartbeat=5,
        )
        self.queue = JsonQueue(**self.conn_params, delegate=self.get_consumer())
        self.mock_connection()

    def tearDown(self):
        self._connect_patch.stop()

    def mock_connection(self):
        class SubscriptableAsyncMock(AsyncMock):
            def __getitem__(_, item):
                if item == "consumer_tag":
                    return self.consumer_tag
                raise NotImplementedError

        self._transport = AsyncMock(name="transport")
        self._protocol = AsyncMock(name="protocol", close=AsyncMock())
        self._protocol.channel = SubscriptableAsyncMock(
            return_value=AsyncMock(
                publish=AsyncMock(),
                basic_qos=AsyncMock(),
                basic_consume=AsyncMock(),
            )
        )
        mocked_connection = AsyncMock(
            return_value=[self._transport, self._protocol]
        )
        self._connect_patch = patch.object(
            aioamqp, "connect", mocked_connection
        )
        self._connect = self._connect_patch.start()

    def get_consumer(self) -> QueueConsumerDelegate:
        return AsyncMock()
