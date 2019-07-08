Início rápido
=============

Um exemplo rápido para mostrar a ideia geral do asynworker.

.. code:: python

  from asyncworker import App, RouteTypes
  from aiohttp import web


  app = App()

  @app.route(["/"], type=RouteTypes.HTTP, methods=["GET"])
  async def handler(req: web.Request):
    return web.json_response({})

Esse código é possível ser rodado na linha de comando e é capaz de atendar a uma requisição HTTP assim:

.. code:: shell

  curl http://127.0.0.1:8080/
