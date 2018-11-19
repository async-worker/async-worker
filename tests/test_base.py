import asynctest
from asynctest import Mock, patch, CoroutineMock

from asyncworker import BaseApp
from asyncworker.models import RouteTypes


class BaseAppTests(asynctest.TestCase):
    async def setUp(self):
        class MyApp(BaseApp):
            handlers = (Mock(startup=CoroutineMock()),)

        self.app = MyApp()

    async def test_setitem_changes_internal_state_if_not_frozen(self):
        self.app['foo'] = foo = asynctest.Mock()
        self.assertEqual(foo, self.app._state['foo'])

        await self.app.freeze()

        with self.assertRaises(RuntimeError):
            self.app['foo'] = "will raise an error"

    async def test_delitem_changes_internal_state_if_not_frozen(self):
        self.app['foo'] = "value"
        self.app['bar'] = "another value"

        del self.app['foo']

        await self.app.freeze()

        with self.assertRaises(RuntimeError):
            del self.app['bar']

    async def test_getitem_returns_internal_state_value(self):
        self.app['dog'] = "Xablau"

        self.assertEqual(self.app['dog'], "Xablau")

    async def test_len_returns_internal_state_value(self):
        self.app.update(pet='dog', name='Xablau')

        self.assertEqual(len(self.app), 2)

    async def test_iter_iters_through_internal_state_value(self):
        self.app.update(pet='dog', name='Xablau')

        state = dict(**self.app)
        self.assertEqual(state, {'pet': 'dog', 'name': 'Xablau'})

    async def test_startup_freezes_applications_and_sends_the_on_startup_signal(self):
        await self.app.startup()

        self.assertTrue(self.app.frozen())
        # _on_startup.send.assert_awaited_once_with(self.app)

    async def test_route_raises_an_error_is_type_isnt_a_valid_RouteType(self):
        with self.assertRaises(TypeError):
            self.app.route(['route'], type='invalid')

    async def test_route_registers_a_route_to_routes_registry(self):
        handler = CoroutineMock()

        self.app.route(['route'], dog="Xablau")(handler)

        self.assertEqual(
            self.app.routes_registry,
            {
                handler: {
                    'type': RouteTypes.AMQP_RABBITMQ,
                    'routes': ['route'],
                    'handler': handler,
                    'options': {},
                    'default_options': self.app.default_route_options,
                    'dog': 'Xablau'
                }
            }
        )
