import abc
from collections import UserList


class Freezable(metaclass=abc.ABCMeta):
    def frozen(self) -> bool:
        raise NotImplementedError

    async def freeze(self):
        raise NotImplementedError


class Signal(UserList):
    """Coroutine-based signal implementation.

    To connect a callback to a signal, use any list method.

    Signals are fired using the send() coroutine, which takes named
    arguments.
    """

    def __init__(self, owner: Freezable) -> None:
        super().__init__()
        self._owner = owner
        self.frozen = False

    def __repr__(self):
        return "<Signal owner={}, frozen={}, {!r}>".format(
            self._owner, self.frozen, list(self)
        )

    async def send(self, *args, **kwargs):
        """
        Sends data to all registered receivers.
        """
        if self.frozen:
            raise RuntimeError("Cannot send on frozen signal.")

        for receiver in self:
            await receiver(*args, **kwargs)

        self.frozen = True
        await self._owner.freeze()
