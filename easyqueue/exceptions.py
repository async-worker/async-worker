class EmptyQueueException(Exception):
    """No message to get"""


class UndecodableMessageException(Exception):
    """Can't decode as JSON"""


class InvalidMessageSizeException(ValueError):
    def __init__(self, message):
        """
        Message size if bigger than it should be
        :type message: amqp.Message
        """
        self.message = message
