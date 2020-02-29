HTTP
====

.. versionadded:: 0.6.0

Aqui mostraremos como escrever um handler que é estimulado através de requisições HTTP.


Um handler é simplesmete uma corotina que recebe um request (``aiohttp.web.Request``) e retorna uma response (``aiohttp.web.Response``). Essa corotina passa a ser um handler "asyncworker" quando é decorada com ``@app.route()``, onde ``app`` é uma instância de ``asyncworker.App``.

Vejamos um handler bem simples que apenas retorna ``HTTP 200 OK``.

.. code:: python

  @app.route(["/"], type=RouteTypes.HTTP, methods=["GET"])
  async def handler(req: web.Request):
    return web.json_response({})


Como recebemos um request do aiohttp, podemos fazer o que for preciso para extrair dele as informações que precisarmos. Para mais detalhes, veja a doc do aiohttp: https://docs.aiohttp.org/en/stable/web.html


.. toctree::
   :maxdepth: 5
   :titlesonly:

   doc.rst
