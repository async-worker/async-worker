
from asynctest import TestCase

from asyncworker.sse.message import SSEMessage

class SSEMessageTest(TestCase):

    async def test_init_with_body(self):
        event_name = "group_changed"
        event_body = {"id": "mygroup", "value": "other-value"}
        message = SSEMessage(event_name, event_body)
        self.assertEqual(event_name, message.name)
        self.assertEqual(event_body, message.body)
        
