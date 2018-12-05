import logging

from pydantic import BaseSettings
from simple_json_logger import JsonLogger


class Settings(BaseSettings):
    LOGLEVEL: str = "ERROR"

    AMQP_DEFAULT_VHOST: str = "/"

    HTTP_HOST: str = "127.0.0.1"
    HTTP_PORT: int = 8080

    class Config:
        allow_mutation = False
        env_prefix = "ASYNCWORKER_"


settings = Settings()

logger = JsonLogger(flatten=True)
logger.setLevel(getattr(logging, settings.LOGLEVEL, logging.INFO))
