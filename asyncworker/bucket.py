from typing import List, Any


class Bucket:

    def __init__(self, size: int) -> None:
        self.size = size
        # fixme: Criar uma interface comum para as *Message para substituir esse Any
        self._items: List[Any] = []

    def is_full(self) -> bool:
        return len(self._items) == self.size

    def put(self, item):
        if self.is_full():
            raise BucketFullException(f"Bucket is at full capacity: {self.size}")
        self._items.append(item)

    def pop_all(self):
        _r = self._items
        self._items = []
        return _r

    @property
    def used(self) -> int:
        return len(self._items)


class BucketFullException(Exception):
    pass
