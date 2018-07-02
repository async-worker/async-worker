from enum import Enum, auto

class Options(Enum):
    BULK_SIZE = auto()
    BULK_FLUSH_INTERVAL = auto()


class Defaultvalues:
    BULK_SIZE = 1
    BULK_FLUSH_INTERVAL = 60
