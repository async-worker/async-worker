import json
import types
import unittest
from unittest.mock import patch, call, ANY
import amqp

from easyqueue.queue import ExternalQueue, DeliveryModes
from easyqueue.exceptions import EmptyQueueException, \
    UndecodableMessageException, InvalidMessageSizeException


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.Connection_patcher = patch.object(amqp, 'Connection')
        self.Connection = self.Connection_patcher.start()

        self.channel = self.Connection.return_value.channel.return_value

        self.queue = ExternalQueue(host='ip-address',
                                   username='guest',
                                   password='passwd',
                                   queue_name='some_queue',
                                   exchange='fetcher',
                                   virtual_host='/dummy-virtual-host')

    def tearDown(self):
        self.Connection_patcher.stop()

    def test_connects_with_correct_args(self):
        expected = call(heartbeat=60,
                        host='ip-address',
                        userid='guest',
                        password='passwd',
                        virtual_host='/dummy-virtual-host')

        self.assertEqual([expected], amqp.Connection.call_args_list)

    def test_supports_context(self):
        with self.queue as q:
            self.assertEqual(q, self.queue)

    def test_closes_connects_exiting_context(self):
        with self.queue as q: pass
        self.assertEqual([call()], self.Connection.return_value.close.call_args_list)

    def test_close_connection(self):
        self.queue.close()
        self.assertEqual([call()], self.Connection.return_value.close.call_args_list)

    def test_puts_with_correct_params(self):
        self.queue.exchange = 'egg'
        self.queue.put(body={}, routing_key='spam', priority=10)

        self.assertEqual([call(exchange='egg', routing_key='spam', msg=ANY)],
                         self.channel.basic_publish.call_args_list)

    def test_puts_message_with_string_body(self):
        self.queue.put(body='spam', routing_key='api', priority=10)

        actual_message = self.channel.basic_publish.call_args_list[0][1]['msg']
        expected_message = self._make_message('spam', priority=10)

        self._assertPropertiesEqual(
            expected_message, actual_message,
            'body', 'delivery_mode', 'content_type', 'priority')

    def test_puts_message_with_dict_body(self):
        self.queue.put({'my mock': 'message'}, routing_key='api', priority=10)

        actual_message = self.channel.basic_publish.call_args_list[0][1]['msg']
        expected_message = self._make_message({'my mock': 'message'},
                                              priority=10)

        self._assertPropertiesEqual(
            expected_message, actual_message,
            'body', 'delivery_mode', 'content_type', 'priority')

    def test_puts_raw_message(self):
        message = self._make_message('spam')
        self.queue.put(body=message, routing_key='api', priority=10)

        actual_message = self.channel.basic_publish.call_args_list[0][1]['msg']

        self.assertEqual(message, actual_message)

    def test_put_accepts_exchange(self):
        self.queue.put(body='', routing_key='wow', exchange='yay')

        self.assertEqual([call(msg=ANY, exchange='yay', routing_key='wow')],
                         self.channel.basic_publish.call_args_list)

    def test_rejects_message(self):
        self.queue.reject(delivery_tag=10)

        self.assertEqual([call(10, requeue=True)],
                         self.channel.basic_reject.call_args_list)

    def test_gets_message(self):
        mocked_message = self.channel.basic_get.return_value = \
            self._make_message({'name': 'josé'}, delivery_tag=99)

        expected_body, expected_delivery_tag = \
            json.loads(mocked_message.body), mocked_message.delivery_tag
        actual_body, actual_delivery_tag = self.queue.get()

        self.assertEqual(expected_body, actual_body)
        # delivery_tag is configured via channel.basic_get,
        # which we're mocking, hence we're not testing it properly
        self.assertEqual(expected_delivery_tag, actual_delivery_tag)

    def test_gets_message_in_bytes(self):
        mocked_message = self.channel.basic_get.return_value = \
            self._make_message(b'{"name":"jose"}')

        actual_body, _ = self.queue.get()
        expected_body = json.loads(mocked_message.body.decode('utf-8'))

        self.assertEqual(expected_body, actual_body)

    def test_get_raises_error_if_body_cant_be_parsed(self):
        self.queue.redeliver_to_garbage_queue = True
        self.channel.basic_get.return_value =\
            self._make_message('__undecodable__')

        with self.assertRaises(UndecodableMessageException) as ex:
            self.queue.get()

        self.assertEqual(ex.exception.args[0],
                         '"__undecodable__" can\'t be decoded as JSON')
        self.assertEqual([call(exchange='fetcher',
                               routing_key=self.queue.garbage_routing_key,
                               msg=ANY)],
                         self.channel.basic_publish.call_args_list)

    def test_get_republishes_to_garbage_queue_if_body_cant_be_parsed_and_redeliver_to_garbage_queue_is_on(self):
        self.queue.redeliver_to_garbage_queue = True
        message = self._make_message('__undecodable__')
        self.channel.basic_get.return_value = message

        self.assertRaises(UndecodableMessageException, self.queue.get)

        expected_message = message
        actual_message = self.channel.basic_publish.call_args_list[0][1]['msg']

        self.assertEqual(expected_message.body, actual_message.body)

    def test_get_doesnt_republish_to_garbage_queue_if_body_cant_be_parsed_and_redeliver_to_garbage_queue_is_off(self):
        self.queue.redeliver_to_garbage_queue = False
        self.channel.basic_get.return_value =\
            self._make_message('__undecodable__')

        self.assertRaises(UndecodableMessageException, self.queue.get)

        self.assertEqual([], self.channel.basic_publish.call_args_list)

    def test_get_raises_empty_queue_error_if_no_message_is_returned(self):
        self.channel.basic_get.return_value = None
        self.assertRaises(EmptyQueueException, self.queue.get)

    def test_getmany_returns_generator_with_messages_from_queue(self):
        messages = [self._make_message('{"a":"%s"}' % i)
                    for i in ('spam', 'ham',)]
        self.channel.basic_get.side_effect = messages

        expected = (({'a': 'spam'}, 0), ({'a': 'ham'}, 0),)
        actual = self.queue.get_many(2)

        self.assertIsInstance(actual, types.GeneratorType)
        self.assertEqual(expected, tuple(actual))

    def test_getmany_returns_less_than_total_messages_from_queue(self):
        messages = [self._make_message('{"a":"%s"}' % i)
                    for i in ('spam', 'ham',)]
        self.channel.basic_get.side_effect = messages

        expected = (({'a': 'spam'}, 0),)
        actual = self.queue.get_many(1)

        self.assertEqual(expected, tuple(actual))

    def test_getmany_stops_when_there_is_no_message_left(self):
        messages = [self._make_message('{"a":"%s"}' % i)
                    for i in ('spam', 'ham',)]
        self.channel.basic_get.side_effect = messages + [None]

        expected = (({'a': 'spam'}, 0), ({'a': 'ham'}, 0),)
        actual = self.queue.get_many(100)

        self.assertEqual(expected, tuple(actual))

    def test_ack_message(self):
        self.queue.ack(99)
        self.assertEqual([call(99)], self.channel.basic_ack.call_args_list)

    def test_it_enforces_max_length_for_message(self):
        body = json.dumps({
            'i_will_be_bigger_than_max_length': 666,
            'why are you wasting your time reading me?': 999,
            'really!? Get a life!': ''
        })
        message = self._make_message(body)

        self.queue.max_message_length = len(body) - 1
        self.channel.basic_get.side_effect = [message]
        with self.assertRaises(InvalidMessageSizeException):
            self.queue.get()

    def test_InvalidMessageSizeException_is_raised_with_unparsed_message(self):
        body = json.dumps({
            'will you ever learn?': 666,
            'stop reading me': 999,
            "Who's crazier? I wrote that shit, but you're reading it!": 'you'
        })
        message = self._make_message(body)

        self.queue.max_message_length = len(body) - 1
        self.channel.basic_get.side_effect = [message]

        try:
            self.queue.get()
        except InvalidMessageSizeException as e:
            exception_msg = e.message
            self.assertIsInstance(exception_msg, amqp.Message)
            self.assertIsInstance(exception_msg.body, str)

    def _make_message(self, body,
                      delivery_mode=DeliveryModes.PERSISTENT,
                      content_type='application/json',
                      priority=10,
                      delivery_tag=0):
        message = amqp.Message(json.dumps(body)
                               if isinstance(body, dict) else body,
                               delivery_mode=delivery_mode,
                               content_type=content_type,
                               priority=priority)

        # We use "delivery_tag" thoughout the tests
        setattr(message, 'delivery_info', {'delivery_tag': delivery_tag})

        return message

    def _assertPropertiesEqual(self, expected: object, actual: object, *properties: str):
        for property in properties:
            self.assertEqual(getattr(expected, property),
                             getattr(actual, property))
