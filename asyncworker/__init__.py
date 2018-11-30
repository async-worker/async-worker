from asyncworker.base import BaseApp
from asyncworker.consumer import Consumer
from asyncworker.options import Options, Defaultvalues, Events, RouteTypes
from asyncworker.signals.handlers.http import HTTPServer
from asyncworker.signals.handlers.rabbitmq import RabbitMQ


class App(BaseApp):
    handlers = (RabbitMQ(), HTTPServer())

    def __init__(self, host, user, password, prefetch_count):
        super(App, self).__init__()
        self.host = host
        self.user = user
        self.password = password
        self.prefetch_count = prefetch_count
