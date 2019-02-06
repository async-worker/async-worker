import asyncio
import datetime

import asynctest
from asynctest import CoroutineMock, patch, Mock, call
from freezegun import freeze_time

from asyncworker.time import ClockTicker


class ClockTickerTests(asynctest.TestCase):
    async def test_a_stoped_clock_cannot_be_reused(self):
        clock = ClockTicker(seconds=0.0001)

        async for tick in clock:
            await clock.stop()

        with self.assertRaises(RuntimeError):
            async for tick in clock:
                self.fail("Shouldnt be possible to iter on a stopped clock")

    @freeze_time("2006-06-06 06:06:06")
    async def test_now_should_return_the_current_time_in_secods(self):
        clock = ClockTicker(seconds=1)
        self.assertIsInstance(clock.now(), int)
        self.assertEqual(clock.now(), 1_149_573_966)

    async def test_anext_waits_for_a_tick(self):
        clock = ClockTicker(seconds=0.1)

        with patch.object(
            clock, "_should_iter", side_effect=[False, True, StopAsyncIteration]
        ), patch("asyncworker.time.asyncio.Event.wait") as wait:
            async for tick in clock:
                print(tick)
            wait.assert_awaited_once()

    async def test_it_should_iter_if_current_time_is_a_valid_interval(self):
        with freeze_time("2006-06-06 06:06:06") as frozen_datetime:
            clock = ClockTicker(seconds=2)
            self.assertTrue(clock._should_iter())

            self.assertFalse(clock._should_iter())

            frozen_datetime.tick(delta=datetime.timedelta(seconds=2))
            self.assertTrue(clock._should_iter())

    async def test_it_shouldnt_iter_if_current_time_is_a_valid_interval(self):
        with freeze_time("2006-06-06 06:06:06") as frozen_datetime:
            clock = ClockTicker(seconds=2)
            self.assertTrue(clock._should_iter())

            frozen_datetime.tick(delta=datetime.timedelta(seconds=3))
            self.assertFalse(clock._should_iter())

    async def test_stop_stops_the_current_clock_ticker(self):
        clock = ClockTicker(seconds=2)
        clock._running = True
        _main_task = CoroutineMock()
        with asynctest.patch.object(clock, "_main_task", _main_task()):
            await clock.stop()

            _main_task.assert_awaited_once()
            self.assertFalse(clock._running)

    async def test_run_should_set_the_tick_event_everytime_an_interval_is_passed(
        self
    ):
        event = Mock()
        with patch("asyncworker.time.asyncio.Event", return_value=event):

            async def tick_check(clock: ClockTicker):
                event.set.assert_called_once()
                event.clear.assert_not_called()
                await clock.stop()

            clock = ClockTicker(seconds=2)
            sleep = CoroutineMock(side_effect=lambda seconds: tick_check(clock))

            with patch("asyncworker.time.asyncio.sleep", sleep):
                clock._running = True
                task = self.loop.create_task(clock._run())
                await task
                event.clear.assert_called_once()
                sleep.assert_awaited_once_with(2)
