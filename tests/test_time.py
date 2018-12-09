import asynctest
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

    @freeze_time('2006-06-06 06:06:06')
    async def test_now_should_return_the_current_time_in_secods(self):
        clock = ClockTicker(seconds=1)
        self.assertIsInstance(clock.now(), int)
        self.assertEqual(clock.now(), 1149573966)

    async def test_it_should_iter_if_current_time_is_a_valid_interval(self):
        pass

    async def test_it_shouldnt_iter_if_current_time_is_a_valid_interval(self):
        pass

    async def test_stop_stops_the_current(self):
        pass

    async def test_run_should_set_the_tick_event_everytime_an_interval_is_passed(self):
        pass

