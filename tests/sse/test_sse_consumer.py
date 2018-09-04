from asynctest import TestCase
from asynctest.mock import CoroutineMock
import asynctest
import aiohttp

from aioresponses import aioresponses

from asyncworker.sse.consumer import SSEConsumer


class SSEConsumerTest(TestCase):


    def total_loops(self, n):
        return [True] * n + [False]

    @asynctest.skip("aiohttp não está seguindo esse redirect do aioresponses")
    async def test_follow_redirect(self):
        content = open("./tests/fixtures/sse/single-event.txt").read()
        consumer = SSEConsumer("http://localhost:8081/v2/events")

        with asynctest.patch.object(consumer, 'keep_runnig', side_effect=[True, False]), \
                asynctest.patch.object(consumer, "on_event") as on_event_mock:
            with aioresponses() as m:
                m.get("http://localhost:8081/v2/events", status=301, headers={"Location": "http://localhost:8080/v2/events"})
                m.get("http://localhost:8080/v2/events", status=200, body=content)
                __import__('ipdb').set_trace()
                await consumer.start()
                args_list = on_event_mock.await_args_list
                self.assertEqual([asynctest.mock.call(b'event_stream_attached',
                                                      b'{"remoteAddress":"172.18.0.1","eventType":"event_stream_attached","timestamp":"2018-09-03T18:03:45.685Z"}')], args_list)

    async def test_call_on_event_when_sse_event_is_found(self):
        """
        A cada par de linhas:
            event: ...
            data: ...
        Chamamos o método `on_event()`
        """
        content = open("./tests/fixtures/sse/single-event.txt").read()
        consumer = SSEConsumer("http://localhost:8080/v2/events")

        with asynctest.patch.object(consumer, 'keep_runnig', side_effect=[True, False]), \
                asynctest.patch.object(consumer, "on_event") as on_event_mock:
            with aioresponses() as m:
                m.get("http://localhost:8080/v2/events", status=200, body=content)
                await consumer.start()
                args_list = on_event_mock.await_args_list
                self.assertEqual([asynctest.mock.call(b'event_stream_attached',
                                                      b'{"remoteAddress":"172.18.0.1","eventType":"event_stream_attached","timestamp":"2018-09-03T18:03:45.685Z"}')], args_list)

    async def test_call_on_event_ignore_blank_lines(self):
        content = open("./tests/fixtures/sse/multi-event-blanklines-in-between.txt").read()
        consumer = SSEConsumer("http://localhost:8080/v2/events")

        with asynctest.patch.object(consumer, 'keep_runnig', side_effect=[True, False]), \
                asynctest.patch.object(consumer, "on_event") as on_event_mock:
            with aioresponses() as m:
                m.get("http://localhost:8080/v2/events", status=200, body=content)
                await consumer.start()
                self.assertEqual(4, on_event_mock.await_count)
                args_list = on_event_mock.await_args_list

                event_1 = (
                    b"group_change_success",
                    b'{"groupId":"/asgard-dev","version":"2018-09-04T12:58:57.000Z","eventType":"group_change_success","timestamp":"2018-09-04T12:58:57.072Z"}'
                )

                event_2 =(
                    b"api_post_event",
                    b'{"clientIp":"172.18.0.1","uri":"/v2/apps//asgard-dev/bla","appDefinition":{"id":"/asgard-dev/bla","cmd":"sleep 1000","args":null,"user":null,"env":{},"instances":0,"cpus":1,"mem":128,"disk":0,"gpus":0,"executor":"","constraints":[],"uris":[],"fetch":[],"storeUrls":[],"backoffSeconds":1,"backoffFactor":1.15,"maxLaunchDelaySeconds":3600,"container":{"type":"DOCKER","volumes":[],"docker":{"image":"alpine","network":"BRIDGE","portMappings":[],"privileged":false,"parameters":[],"forcePullImage":false}},"healthChecks":[],"readinessChecks":[],"dependencies":[],"upgradeStrategy":{"minimumHealthCapacity":1,"maximumOverCapacity":1},"labels":{},"ipAddress":null,"version":"2018-09-04T12:58:57.000Z","residency":null,"secrets":{},"taskKillGracePeriodSeconds":null,"unreachableStrategy":{"inactiveAfterSeconds":0,"expungeAfterSeconds":0},"killSelection":"YOUNGEST_FIRST","ports":[10006],"portDefinitions":[{"port":10006,"protocol":"tcp","name":"default","labels":{}}],"requirePorts":false,"versionInfo":{"lastScalingAt":"2018-09-04T12:58:57.000Z","lastConfigChangeAt":"2018-09-04T12:56:56.861Z"}},"eventType":"api_post_event","timestamp":"2018-09-04T12:58:57.073Z"}'
                )

                event_3 =(
                    b"status_update_event",
                    b'{"slaveId":"40cf614e-b392-4d31-9230-090ca3c7aa83-S0","taskId":"asgard-dev_bla.0139427f-b042-11e8-9638-0242ac12001f","taskStatus":"TASK_KILLED","message":"Container exited with status 137","appId":"/asgard-dev/bla","host":"172.18.0.51","ipAddresses":[{"ipAddress":"172.17.0.4","protocol":"IPv4"}],"ports":[30989],"version":"2018-09-04T12:56:56.861Z","eventType":"status_update_event","timestamp":"2018-09-04T12:59:57.728Z"}'    
                )

                event_4 =(
                    b"instance_changed_event",
                    b'{"instanceId":"asgard-dev_bla.marathon-0139427f-b042-11e8-9638-0242ac12001f","condition":"Killed","runSpecId":"/asgard-dev/bla","agentId":"40cf614e-b392-4d31-9230-090ca3c7aa83-S0","host":"172.18.0.51","runSpecVersion":"2018-09-04T12:56:56.861Z","timestamp":"2018-09-04T12:59:57.739Z","eventType":"instance_changed_event"}'
                )

                self.assertEqual([
                    asynctest.mock.call(*event_1),
                    asynctest.mock.call(*event_2),
                    asynctest.mock.call(*event_3),
                    asynctest.mock.call(*event_4),
                ], args_list)


    async def test_reconnect_if_disconnected(self):
        session_mock = CoroutineMock(get=CoroutineMock(side_effect=["", aiohttp.ClientError(), aiohttp.ClientError()]))
        consumer = SSEConsumer("http://localhost:8080/v2/events")
        consumer.session = session_mock

        with asynctest.patch.object(consumer, 'keep_runnig', side_effect=[True, True, True, False]), \
                asynctest.patch.object(consumer, "_consume_events", side_effect=CoroutineMock()) as consume_events_mock:
            await consumer.start()
            self.assertEqual(1, consume_events_mock.await_count)
            self.assertEqual(3, session_mock.get.call_count)
            self.assertEqual(1, session_mock.get.await_count)
                
    async def test_consume_again_if_reconnected(self):
        session_mock = CoroutineMock(get=CoroutineMock(side_effect=["", aiohttp.ClientError(), ""]))
        consumer = SSEConsumer("http://localhost:8080/v2/events")
        consumer.session = session_mock

        with asynctest.patch.object(consumer, 'keep_runnig', side_effect=[True, True, True, False]), \
                asynctest.patch.object(consumer, "_consume_events", side_effect=CoroutineMock()) as consume_events_mock:
            await consumer.start()
            self.assertEqual(2, consume_events_mock.await_count)
            self.assertEqual(3, session_mock.get.call_count)
            self.assertEqual(2, session_mock.get.await_count)

    async def test_call_on_connection_error(self):
        """
        Call on_connection_error when an aiohttp.ClientError is raised
        """
        session_mock = CoroutineMock(get=CoroutineMock(side_effect=[aiohttp.ClientError()]))
        consumer = SSEConsumer("http://localhost:8080/v2/events")
        consumer.session = session_mock

        with asynctest.patch.object(consumer, 'keep_runnig', side_effect=self.total_loops(1)), \
                asynctest.patch.object(consumer, "on_connection_error", side_effect=CoroutineMock()) as on_connection_error_mock:
            await consumer.start()
            self.assertEqual(1, on_connection_error_mock.await_count)

    async def test_call_on_exception(self):
        """
        Call on_exceptin when an unhandled exception is raised
        """

        content = open("./tests/fixtures/sse/single-event.txt").read()
        consumer = SSEConsumer("http://localhost:8080/v2/events")

        with asynctest.patch.object(consumer, 'keep_runnig', side_effect=self.total_loops(1)), \
                asynctest.patch.object(consumer, "on_event", side_effect=Exception()), \
                asynctest.patch.object(consumer, "on_exception", side_effect=CoroutineMock()) as on_exception_mock:
            with aioresponses() as m:
                m.get("http://localhost:8080/v2/events", status=200, body=content)
                await consumer.start()
                self.assertEqual(1, on_exception_mock.await_count)

    async def test_reconect_if_unhandled_reconnected(self):
        session_mock = CoroutineMock(get=CoroutineMock(side_effect=["", Exception()]))
        consumer = SSEConsumer("http://localhost:8080/v2/events")
        consumer.session = session_mock

        with asynctest.patch.object(consumer, 'keep_runnig', side_effect=[True, True, False]), \
                asynctest.patch.object(consumer, "_consume_events", side_effect=CoroutineMock()) as consume_events_mock:
            await consumer.start()
            self.assertEqual(1, consume_events_mock.await_count)
            self.assertEqual(2, session_mock.get.call_count)
            self.assertEqual(1, session_mock.get.await_count)

    async def test_flush_bucket_on_connection_error(self):
        """
        Sempre que o stream acabar, ou formos desconectados
        temos que fazer flush do bucket.
        """
        self.fail()
