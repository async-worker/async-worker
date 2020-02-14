import logging

from aiologger.loggers.json import JsonLogger
from pydantic import BaseSettings

from asyncworker.options import DefaultValues


class Settings(BaseSettings):
    LOGLEVEL: str = "ERROR"

    AMQP_DEFAULT_VHOST: str = "/"
    AMQP_DEFAULT_PREFETCH_COUNT: int = 128
    AMQP_DEFAULT_HEARTBEAT: int = 60

    HTTP_HOST: str = "127.0.0.1"
    HTTP_PORT: int = 8080

    FLUSH_TIMEOUT: int = DefaultValues.BULK_FLUSH_INTERVAL

    class Config:
        allow_mutation = False
        env_prefix = "ASYNCWORKER_"


settings = Settings()

loglevel = getattr(logging, settings.LOGLEVEL, logging.INFO)
logger = JsonLogger.with_default_handlers(level=loglevel, flatten=True)
