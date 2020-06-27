from aioamqp.protocol import OPEN
from asynctest import TestCase

from asyncworker.easyqueue.queue import JsonQueue, _ensure_connected


class EnsureConnectedTest(TestCase):
    async def setUp(self):
        self.queue = JsonQueue(
            host="127.0.0.1", username="guest", password="guest"
        )
        self.wrapped = _ensure_connected(self._func)

    async def _func(self, arg1):
        return 42

    async def tearDown(self):
        await self.queue.connection.close()

    async def test_create_new_channel_if_channel_is_closed(self):
        await self.wrapped(self.queue)

        await self.queue.connection.channel.close()

        channel, proto, transp = (
            self.queue.connection.channel,
            self.queue.connection._protocol,
            self.queue.connection._transport,
        )

        self.assertEqual(42, await self.wrapped(self.queue))

        self.assertNotEqual(channel, self.queue.connection.channel)
        self.assertEqual(proto, self.queue.connection._protocol)
        self.assertEqual(transp, self.queue.connection._transport)

    async def test_do_nothing_if_protocol_and_channel_are_open(self):
        await self.wrapped(self.queue)

        channel, proto, transp = (
            self.queue.connection.channel,
            self.queue.connection._protocol,
            self.queue.connection._transport,
        )

        self.assertEqual(42, await self.wrapped(self.queue))

        self.assertEqual(channel, self.queue.connection.channel)
        self.assertEqual(proto, self.queue.connection._protocol)
        self.assertEqual(transp, self.queue.connection._transport)

    async def test_recreate_connected_if_protocol_is_closed(self):
        await self.wrapped(self.queue)

        await self.queue.connection.channel.close()
        await self.queue.connection._protocol.close()
        channel, proto, transp = (
            self.queue.connection.channel,
            self.queue.connection._protocol,
            self.queue.connection._transport,
        )

        self.assertEqual(42, await self.wrapped(self.queue))

        self.assertNotEqual(channel, self.queue.connection.channel)
        self.assertNotEqual(proto, self.queue.connection._protocol)
        self.assertNotEqual(transp, self.queue.connection._transport)
        self.assertTrue(self.queue.connection.channel.is_open)
        self.assertEqual(self.queue.connection._protocol.state, OPEN)
