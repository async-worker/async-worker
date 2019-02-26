import logging

from pydantic import BaseSettings
from aiologger.loggers.json import JsonLogger


class Settings(BaseSettings):
    LOGLEVEL: str = "ERROR"

    AMQP_DEFAULT_VHOST: str = "/"

    HTTP_HOST: str = "127.0.0.1"
    HTTP_PORT: int = 8080

    FLUSH_TIMEOUT: int = 60

    class Config:
        allow_mutation = False
        env_prefix = "ASYNCWORKER_"


settings = Settings()

loglevel = getattr(logging, settings.LOGLEVEL, logging.INFO)
logger = JsonLogger.with_default_handlers(level=loglevel, flatten=True)
