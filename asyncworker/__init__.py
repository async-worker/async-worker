from asyncworker.base import BaseApp
from asyncworker.consumer import Consumer
from asyncworker.options import Options, Defaultvalues, Events
from asyncworker.signal_handlers.rabbitmq import RabbitMQ


class App(BaseApp):
    handlers = (RabbitMQ(),)

    def __init__(self, host, user, password, prefetch_count):
        super(App, self).__init__()
        self.host = host
        self.user = user
        self.password = password
        self.prefetch_count = prefetch_count
