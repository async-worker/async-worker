

Regras para criação de um handler HTTP
======================================

Todo handler HTTP deve seguir algumas regras:

 - Deve sempre ser decorato com :ref:`@app.route() <asyncworker-app-handler>`
 - Deve declarar seus parametros sempre com definição de tipos, pois é assim que o asyncworker saberá passar :ref:`parametros dinâmicos <handler-path-param>` para o handler.
 - Um handler pode não receber nenhum parâmetro. Para isso basta a assinatura do handler ser vazia.

Alguns objetos já são passados so handler, caso estejam presentes em sua assinatura.  Eles são:

 - Uma instância de ``aiohttp.web.Request``.


Parametrização do decorator route() para handlers HTTP
=======================================================

Para um handler HTTP deveremos passar os seguintes parametros para o decorator ``route()``:

  - Lista de paths que devem estar na Request HTTP para que esse handler seja chamado;
  - ``type=RouteTypes.HTTP``
  - ``methods`` sendo uma lista de métodos HTTP permitidos para esse handler

Parametros no path podem ser definidos cercando com ``{}``, ex: ``/users/{user_id}``. Mais delathes em como receber esses valores em seu handler :ref:`aqui <handler-path-param>`.


ENVs para escolher a porta e o IP onde o server http estará escutando
========================================================================


Por padrão, fazemos o binding em ``127.0.0.1``, porta ``8080``, mas isso pode ser alterado com as envvars ``ASYNCWORKER_HTTP_HOST`` e ``ASYNCWORKER_HTTP_PORT``, respectivamente.



Handlers que são objetos callable
===========================================

.. versionadded:: 0.11.4

É possível também escrever handlers como objetos que são callables, ou seja, possuem o método ``async def __call__()``. Importante notar que a assinatura do método ``__call__()`` segue as mesmas regras da assinatura de uma corotina decorada com o ``@app.route()``.

Esses handlers são especialmente úteis quando você precisa guardar algum tipo de contexto e não quer fazer isso com variáveis globais no nível do módulo.

Um exemplo de um handler:

.. code:: python

  class Handler:
    async def __call__(self, req: web.Request):
      pass


Importante notar que como estamos lidando com um objeto ele precisará ser instanciado antes de ser usado e isso significa que não vamos poder decorá-lo da mesma forma que decoramos handlers que são apenas uma corotina. Um código desse gera erro de sintaxe:

.. code:: python

  class Handler:
    async def __call__(self, req: web.Request):
      pass

  h = Handler()

  @app.route(...)
  h

Por isso esses handlers precisam ser registrados chamando o decorator manualmente, assim:

.. code:: python

  class Handler:
    async def __call__(self, req: web.Request):
      pass

  h = Handler()

  app.route(...)(h)


.. _typed-handlers:

Handlers que recebem mais do que apenas Request
================================================

.. versionadded:: 0.11.0

O asyncworker permite que um handler receba quaisquer prametros. Para isso a assinatura do handler deve conter typehints em todos os parametros. Isso faz com que o asyncowker consiga fazer a resolução desses prametros e consiga chamar o handler corretamente.

Todas as instancias de ``aiohttp.web.Request`` recebem um atributo chamado ``types_registry`` que é do tipo :py:class:`asyncworker.types.registry.TypesRegistry`. Para que um parametro possa ser passado a um handler ele deve ser adicionado a esse registry do request.

Um exemplo de como popular esse registry é através de um decorator aplicado diretamente ao um handler. Vejamos um exemplo:

.. code:: python


  from aiohttp import web
  from myproject.models.user import User
  from http import HTTPStatus


  def auth_required(handler):
      async def _wrapper(request: web.Request):
          basic_auth = request.headers.get("Authorization")
          user = get_authenticated_user(basic_auth)
          if not user:
              return web.json_response({...}, status=HTTPStatus.UNAUTHORIZED)

          request["types_registry"].set(user)
          return await call_http_handler(request, handler)

      return _wrapper

  @app.route(["/"], type=RouteTypes.HTTP, methods=["GET"])
  @auth_required
  async def handler(user: User):
      return web.json_response({})

Aqui o decorator ``auth_required()`` é responsável por fazer a autenticação, pegando dados do Request e encontrando um usuário válido. Se um usuário não puder ser encontrado, retorna ``HTTPStatus.UNAUTHORIZED``. Se um usuário autenticar com sucesso, apenas adiciona o objeto user (que é do tipo ``User``) no registry que está no request. Isso é o suficiente para que o handler, quando for chamado, receba diretamente esse user já autenticado.



Recebendo parâmetros vindos do path do Request
===============================================

.. _handler-path-param:
.. versionadded:: 0.11.5

É possível receber em seu handler parametros definidos no path da requisição. Isso é feito través do decorator :py:func:`asyncworker.http.decorators.parse_path`.

Quando decoramos nosso handler com esse decorator instruímos o asyncworker a tentar extrair parametros do path e passar para nosso handler.

Importante notar que, primeiro o asyncworker vai procurar nosso parametro pelo nome e só depois tentará procurar o tipo.  Exemplo:

.. code-block:: python

  @app.route(["/by_id/{_id}"], type=RouteTypes.HTTP, methods=["GET"])
  @parse_path
  async def by_id(_id: int):
      return web.json_response({})

Nesse caso, como handler está dizendo que precisa de um parametro chamado ``_id`` temos que declarar um parametro de mesmo nome no path da Request. Depois que esse `match` for feito passaremos o valor recebido no path para o construtor do tipo definido na assinatura do handler.

Então nesse caso faremos um simples ``int(<valor>)``. Esse resultado será passado ao handler no parametro ``_id``, no momento da chamada.

Importante notar que só serão passados ao handler os parametros que estão definidos na assinatura. Então se seu path recebe dois parametros e seu handler só se interessa por um deles, basta declarar na assinatura do handler o parametro que você quer receber.


Essa implementação ainda é experimental e servirá de fundação para uma implementação mais complexa, talvez com tipos mais complexos e sem a necessidade de passar o decorator explicitamente.
