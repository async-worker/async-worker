
class Bucket:

    def __init__(self, size):
        self.size = size
        self._items = []

    def is_full(self):
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
    def used(self):
        return len(self._items)


class BucketFullException(Exception):
    pass
