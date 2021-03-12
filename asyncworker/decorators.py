def wraps(original_handler):
    def _wrap(deco):
        if hasattr(original_handler, "__original_annotations__"):
            deco.__original_annotations__ = (
                original_handler.__original_annotations__
            )
        else:
            deco.__original_annotations__ = original_handler.__annotations__
        return deco

    return _wrap
