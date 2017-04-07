class EmptyQueueException(Exception):
    """No message to get"""


class UndecodableMessageException(Exception):
    """Can't decode as JSON"""


class InvalidMessageSizeException(ValueError):
    """Message size if bigger than it should be"""
