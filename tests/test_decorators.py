from asynctest import TestCase

from asyncworker.decorators import wraps


def handler_register(func):
    async def _register_wrap(x: int = 0):
        return func

    return _register_wrap


def _deco(handler):
    @wraps(handler)
    async def _wrapper(s: str, **_):
        pass

    return _wrapper


def _deco2(handler):
    @wraps(handler)
    async def _wrapper(param: bool, i: int, **_):
        pass

    return _wrapper


def _deco3(handler):
    @wraps(handler)
    async def _wrapper(other: str, flag: bool, **_):
        pass

    return _wrapper


class TestWrapsDecorator(TestCase):
    async def test_with_one_first_decorator(self):
        @handler_register
        @_deco
        async def _func(q: int, b: bool):
            pass

        final_func = await _func()
        self.assertEqual(final_func.__annotations__, {"s": str})
        self.assertEqual(
            final_func.__original_annotations__, {"q": int, "b": bool}
        )

    async def test_with_two_second_decorators(self):
        @handler_register
        @_deco2
        @_deco
        async def _func(other: int, integer: int, feature: bool):
            pass

        final_func = await _func()
        self.assertEqual(final_func.__annotations__, {"param": bool, "i": int})
        self.assertEqual(
            final_func.__original_annotations__,
            {"other": int, "integer": int, "feature": bool},
        )

    async def test_with_three_decorators(self):
        @handler_register
        @_deco3
        @_deco2
        @_deco
        async def _func(other: int, integer: int, feature: bool):
            pass

        final_func = await _func()
        self.assertEqual(
            final_func.__annotations__, {"flag": bool, "other": str}
        )
        self.assertEqual(
            final_func.__original_annotations__,
            {"other": int, "integer": int, "feature": bool},
        )

    async def test_when_decorator_has_parameters(self):
        def _deco_with_params(a: int):
            def _wrap1(handler):
                @wraps(handler)
                async def _final_wrap(param: bool, **_):
                    pass

                return _final_wrap

            return _wrap1

        @handler_register
        @_deco_with_params(42)
        async def _func(x: bool, y: int):
            pass

        final_func = await _func()
        self.assertEqual(final_func.__annotations__, {"param": bool})
        self.assertEqual(
            final_func.__original_annotations__, {"x": bool, "y": int}
        )

    async def test_call_chain_one_decorator(self):
        self.fail()

    async def test_call_chain_two_decorators(self):
        self.fail()

    async def test_call_chain_three_decorators(self):
        self.fail()
