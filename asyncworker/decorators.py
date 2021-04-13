def wraps(original_handler):
    """
    Esse decorator faz com que a assinatura da função original
    "suba" até o último decorator, que deverá ser sempre um registrador do
    próprio asyncworker. ex:
    @app.http.get(...)
    @deco1
    @deco2
    async def handler(...)
        pass

    Nesse caso, os decorators `@deco1` e `@deco2` devem, *necessariamente*
    fazer uso desse `@wraps()`
    """

    def _wrap(deco):
        if hasattr(original_handler, "__original_annotations__"):
            deco.__original_annotations__ = (
                original_handler.__original_annotations__
            )
        else:
            deco.__original_annotations__ = original_handler.__annotations__
        return deco

    return _wrap
