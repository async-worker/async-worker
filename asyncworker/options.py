from enum import Enum, auto


class Options(Enum):
    BULK_SIZE = auto()
    BULK_FLUSH_INTERVAL = auto()
    MAX_CONCURRENCY = auto()


class Actions(Enum):
    ACK = auto()
    REJECT = auto()
    REQUEUE = auto()


class Events(Enum):
    ON_SUCCESS = auto()
    ON_EXCEPTION = auto()


class DefaultValues:
    BULK_SIZE = 1
    BULK_FLUSH_INTERVAL = 60
    ON_SUCCESS = Actions.ACK
    ON_EXCEPTION = Actions.REQUEUE
    RUN_EVERY_MAX_CONCURRENCY = 1


class RouteTypes(Enum):
    AMQP_RABBITMQ = auto()
    SSE = auto()
    HTTP = auto()
