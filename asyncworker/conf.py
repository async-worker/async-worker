import os
import logging

from simple_json_logger import JsonLogger

LOGLEVEL = os.getenv("ASYNCWORKER_LOGLEVEL", "ERROR")

logger = JsonLogger(flatten=True)
logger.setLevel(getattr(logging, LOGLEVEL, logging.INFO))
