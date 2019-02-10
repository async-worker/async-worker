import unittest
from unittest.mock import Mock

from easyqueue.exceptions import UndecodableMessageException
from easyqueue.message import AMQPMessage


class AMQPMessageTests(unittest.TestCase):
    def test_lazy_deserialization_raises_an_error_if_deserialization_fails(
        self
    ):
        data = b"Xablau"
        deserializer = Mock(side_effect=ValueError)

        msg = AMQPMessage(
            connection=Mock(),
            channel=Mock(),
            queue_name=Mock(),
            serialized_data=data,
            delivery_tag=Mock(),
            envelope=Mock(),
            properties=Mock(),
            deserialization_method=deserializer,
        )

        with self.assertRaises(UndecodableMessageException):
            _ = msg.deserialized_data

        deserializer.assert_called_once_with(data)

    def test_successful_deserialization(self):
        data = b'["Xablau"]'
        deserializer = Mock(return_value=["Xablau"])

        msg = AMQPMessage(
            connection=Mock(),
            channel=Mock(),
            queue_name=Mock(),
            serialized_data=data,
            delivery_tag=Mock(),
            envelope=Mock(),
            properties=Mock(),
            deserialization_method=deserializer,
        )

        self.assertEqual(msg.deserialized_data, ["Xablau"])

    def test_deserialization_is_only_called_once(self):
        data = b'["Xablau"]'
        deserializer = Mock(return_value=["Xablau"])

        msg = AMQPMessage(
            connection=Mock(),
            channel=Mock(),
            queue_name=Mock(),
            serialized_data=data,
            delivery_tag=Mock(),
            envelope=Mock(),
            properties=Mock(),
            deserialization_method=deserializer,
        )

        _ = [msg.deserialized_data for _ in range(10)]

        deserializer.assert_called_once_with(data)

    def test_equal_messages(self):
        msg1 = AMQPMessage(
            connection=Mock(),
            channel=Mock(),
            queue_name=Mock(),
            serialized_data=Mock(),
            delivery_tag=Mock(),
            envelope=Mock(),
            properties=Mock(),
            deserialization_method=Mock(),
        )
        msg2 = AMQPMessage(
            connection=msg1.connection,
            channel=msg1.channel,
            queue_name=msg1.queue_name,
            serialized_data=msg1.serialized_data,
            delivery_tag=msg1.delivery_tag,
            envelope=msg1._envelope,
            properties=msg1._properties,
            deserialization_method=msg1._deserialization_method,
        )
        self.assertEqual(msg1, msg2)

    def test_not_equal_messages(self):
        msg1 = AMQPMessage(
            connection=Mock(),
            channel=Mock(),
            queue_name=Mock(),
            serialized_data=Mock(),
            delivery_tag=Mock(),
            envelope=Mock(),
            properties=Mock(),
            deserialization_method=Mock(),
        )

        msg2 = AMQPMessage(
            connection=msg1.connection,
            channel=Mock(),
            queue_name=msg1.queue_name,
            serialized_data=msg1.serialized_data,
            delivery_tag=msg1.delivery_tag,
            envelope=msg1._envelope,
            properties=msg1._properties,
            deserialization_method=msg1._deserialization_method,
        )
        self.assertNotEqual(msg1, msg2)
