import asyncio

import asynctest
from asynctest import Mock, CoroutineMock, patch, call
from signal import Signals

from asyncworker import BaseApp
from asyncworker.options import RouteTypes, DefaultValues, Options
from asyncworker.task_runners import ScheduledTaskRunner


class BaseAppTests(asynctest.TestCase):
    async def setUp(self):
        class MyApp(BaseApp):
            handlers = (
                Mock(startup=CoroutineMock(), shutdown=CoroutineMock()),
            )

        self.appCls = MyApp
        self.app = MyApp()

    async def test_setitem_changes_internal_state_if_not_frozen(self):
        self.app["foo"] = foo = asynctest.Mock()
        self.assertEqual(foo, self.app._state["foo"])

        await self.app.freeze()

        with self.assertRaises(RuntimeError):
            self.app["foo"] = "will raise an error"

    async def test_delitem_changes_internal_state_if_not_frozen(self):
        self.app["foo"] = "value"
        self.app["bar"] = "another value"

        del self.app["foo"]

        await self.app.freeze()

        with self.assertRaises(RuntimeError):
            del self.app["bar"]

    async def test_getitem_returns_internal_state_value(self):
        self.app["dog"] = "Xablau"

        self.assertEqual(self.app["dog"], "Xablau")

    async def test_len_returns_internal_state_value(self):
        self.app.update(pet="dog", name="Xablau")

        self.assertEqual(len(self.app), 2)

    async def test_iter_iters_through_internal_state_value(self):
        self.app.update(pet="dog", name="Xablau")

        state = dict(**self.app)
        self.assertEqual(state, {"pet": "dog", "name": "Xablau"})

    async def test_startup_freezes_applications_and_sends_the_on_startup_signal(
        self
    ):
        await self.app.startup()

        self.assertTrue(self.app.frozen())
        # _on_startup.send.assert_awaited_once_with(self.app)

    async def test_route_raises_an_error_is_type_isnt_a_valid_RouteType(self):
        with self.assertRaises(TypeError):
            self.app.route(["route"], type="invalid")

    async def test_route_registers_a_route_to_routes_registry(self):
        handler = CoroutineMock()

        self.app.route(["route"], type=RouteTypes.AMQP_RABBITMQ, dog="Xablau")(
            handler
        )

        self.assertEqual(
            self.app.routes_registry,
            {
                handler: {
                    "type": RouteTypes.AMQP_RABBITMQ,
                    "routes": ["route"],
                    "handler": handler,
                    "options": {},
                    "default_options": self.app.default_route_options,
                    "dog": "Xablau",
                }
            },
        )

    async def test_run_on_startup_registers_a_coroutine_to_be_executed_on_startup(
        self
    ):
        coro = CoroutineMock()

        self.app.run_on_startup(coro)

        self.assertEqual(coro, self.app._on_startup[-1])

        await self.app.startup()
        coro.assert_awaited_once_with(self.app)

    async def test_startup_calls_user_registered_startup_routines_after_app_signal_handlers_startup(
        self
    ):
        coro = CoroutineMock()

        self.app.run_on_startup(coro)

        self.assertEqual(
            self.app._on_startup,
            [*(handler.startup for handler in self.app.handlers), coro],
        )

    async def test_run_on_shutdown_registers_a_coroutine_to_be_executed_on_shutdown(
        self
    ):
        coro = CoroutineMock()

        self.app.run_on_shutdown(coro)
        self.assertIn(coro, self.app._on_shutdown)

        await self.app.shutdown()
        coro.assert_awaited_once_with(self.app)

    async def test_shutdown_is_registered_as_a_signal_handler(self):
        with patch.object(
            self.loop, "add_signal_handler"
        ) as add_signal_handler:
            app = self.appCls()
            add_signal_handler.assert_has_calls(
                [
                    call(Signals.SIGINT, app.shutdown),
                    call(Signals.SIGTERM, app.shutdown),
                ]
            )

    async def test_shutdown_schedules_on_shutdown_signal_send(self):
        with patch.object(self.app._on_shutdown, "send") as send:
            send.assert_not_awaited()

            shutdown_coro = self.app.shutdown()

            self.assertIsInstance(shutdown_coro, asyncio.Task)
            self.assertFalse(shutdown_coro.done())

            send.assert_not_awaited()

            await shutdown_coro
            send.assert_awaited_once_with(self.app)
            self.assertTrue(shutdown_coro.done())

    async def test_run_every_registers_a_coroutine_to_be_executed_as_a_ScheduledTaskRunner(
        self
    ):
        with patch(
            "asyncworker.base.ScheduledTaskRunner", spec=ScheduledTaskRunner
        ) as Runner:
            seconds = 10
            coro = Mock(start=CoroutineMock(), stop=CoroutineMock())

            self.app.run_every(seconds=seconds)(coro)

            Runner.assert_called_once_with(
                seconds=seconds,
                task=coro,
                app=self.app,
                max_concurrency=DefaultValues.RUN_EVERY_MAX_CONCURRENCY,
            )
            self.assertIn(Runner.return_value.start, self.app._on_startup)
            self.assertIn(Runner.return_value.stop, self.app._on_shutdown)
            self.assertIn(Runner.return_value, self.app["task_runners"])

    async def test_run_every_max_concurrency_can_be_overwritten_with_options(
        self
    ):
        with patch(
            "asyncworker.base.ScheduledTaskRunner", spec=ScheduledTaskRunner
        ) as Runner:
            seconds = 10
            coro = Mock(start=CoroutineMock(), stop=CoroutineMock())

            self.app.run_every(
                seconds=seconds, options={Options.MAX_CONCURRENCY: 666}
            )(coro)

            Runner.assert_called_once_with(
                seconds=seconds, task=coro, app=self.app, max_concurrency=666
            )
