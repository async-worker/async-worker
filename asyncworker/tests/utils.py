def typed_any(cls):
    class Any(cls):
        def __eq__(self, other):
            return isinstance(self, other.__class__)

    return Any()
