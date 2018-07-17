from unittest.mock import patch, Mock

import asynctest as asynctest
from freezegun import freeze_time

from asyncworker.utils import Timeit


class TimeitTests(asynctest.TestCase):
    time = 1149573966.0
    time_plus_1_sec = 1149573967.0

    @freeze_time('2006-06-06 06:06:06')
    async def test_it_marks_starting_times(self):
        coro = asynctest.CoroutineMock()
        async with Timeit(name="Xablau", callback=coro) as timeit:
            self.assertEqual(timeit.start, 1149573966.0)

    @freeze_time('2006-06-06 06:06:07')
    async def test_it_marks_finishing_times(self):
        coro = asynctest.CoroutineMock()
        async with Timeit(name="Xablau", callback=coro) as timeit:
            pass
        self.assertEqual(timeit.finish, 1149573967.0)

    async def test_it_calculates_time_delta(self):
        now = Mock(side_effect=[self.time, self.time_plus_1_sec])
        with patch('asyncworker.utils.now', now):
            async with Timeit(name="Xablau", callback=asynctest.CoroutineMock()) as timeit:
                pass
        self.assertEqual(timeit.time_delta, 1.0)

    async def test_it_calls_callback_on_context_end(self):
        callback = asynctest.CoroutineMock()
        times = [self.time, self.time_plus_1_sec]
        with patch('asyncworker.utils.now', Mock(side_effect=times)):
            async with Timeit(name="Xablau", callback=callback) as timeit:
                callback.assert_not_awaited()
        callback.assert_awaited_once_with(
            name=timeit.name,
            time_delta=timeit.time_delta,
            exc_type=None,
            exc_val=None,
            exc_tb=None)

    async def test_it_calls_callback_with_exc_parameters_if_an_exception_is_raised(self):
        coro = asynctest.CoroutineMock()
        try:
            async with Timeit(name="Xablau", callback=coro) as timeit:
                raise KeyError("Xablau")
        except KeyError as e:
            coro.assert_awaited_once_with(
                name=timeit.name,
                time_delta=timeit.time_delta,
                exc_type=KeyError,
                exc_val=e,
                exc_tb=e.__traceback__
            )

    async def test_it_can_be_used_as_a_decorator(self):
        coro = asynctest.CoroutineMock()
        now = Mock(side_effect=[self.time, self.time_plus_1_sec])

        @Timeit(name='Xablau', callback=coro)
        async def foo():
            pass

        with patch('asyncworker.utils.now', now):
            await foo()

        coro.assert_awaited_once_with(
            name='Xablau',
            time_delta=1.0,
            exc_type=None,
            exc_val=None,
            exc_tb=None
        )
