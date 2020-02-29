.. _custom-decorators:

Aplicando decorators customizados a um handler HTTP
=====================================================

É possível escrever seus próprios decorators e aplicá-los a seus handlers, junto com o decorator ``@app.route``. No entando temos algumas regras:

- O decorator ``@app.route()`` deve estar sempre no topo da lista de decorators de um handler;
- Os decorators intermediários devem sempre usar a função :py:func:`asyncworker.routes.call_http_handler()` no momento de chamar o objeto que estão decorando;
- A inner function retornada pelo decorator deve ser uma corotina;
- A inner function deve receber apenas :py:class:`asyncworker.http.wrapper.RequestWrapper`;
- Essa inner function não deve ser decorada com ``@functools.wraps()``.


Um exemplo simples de decorator:

.. code:: python

  from asyncworker.http.wrapper import RequestWrapper

  def my_handler_decorator(handler):
      async def _wrapper(wrapper: RequestWrapper):
          # Código principal do decorator vem aqui
          return await call_http_handler(wrapper.http_request, handler)

      return _wrapper

A razão para isso é que o asyncworker permite que um handler receba parametros dinâmicos (mais sobre isso adiante) e a função ``call_http_handler()`` é quem tem ciência disso e saberá fazer a resolução correta dos parametros necessários para que o handler seja corretamente chamado.

Esse decorator poderia ser aplicado a um handler assim:


.. code:: python

  @app.route(["/"], type=RouteTypes.HTTP, methods=["GET"])
  @my_handler_decorator
  async def handler():
    return web.json_response({})
