Atualizando sua App Asyncworker
===============================


Se você estivere atualizando para versões pós ``0.6.0`` o melhor a fazer é consultar o changelog de cada uma das vesões.

A lista de todas as versões com cada uma de suas mudanças está :ref:`aqui <changelog>`.


0.5.x -> 0.6.0
---------------

Nessa versão, tornamos obrigatório o uso do Enum ``RouteTypes`` e a
assinatura de ``app.route`` mudou. Ex.:

.. code-block:: python

  from asyncworker.models import RouteTypes

  @app.route(['/sse'], type=RouteTypes.SSE)
  async def event_handler(events):
      pass
