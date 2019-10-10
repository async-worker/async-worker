Backends
========

O asyncworker suporte alguns backends diferentes. Por backend entende-se a
origem do estímulo que será processado pelo seu worker, ou mais
específicamente, por um handler do seu worker.

Atualmente o projeto suporta as seguintes backends:

-  `RabbitMQ`_: Consumo de mensagens AMQP;
-  `Server Side Events`_: Possibilidade de eventos de um endpoint que implementa Server Side Events;
-  `HTTP`_: Possibilidade de receber dados via requisições HTTP

.. _RabbitMQ: https://www.rabbitmq.com/
.. _Server Side Events: https://en.wikipedia.org/wiki/Server-sent_events
.. _HTTP: https://pt.wikipedia.org/wiki/Hypertext_Transfer_Protocol


Consumindo de uma fila no RabbitMQ
----------------------------------

.. code:: python


   from asyncworker import App, RouteTypes
   from asyncworker.connections import AMQPConnection


   amqp_conn = AMQPConnection(host="127.0.0.1", user="guest", password="guest", prefetch_count=256)
   app = App(connections=[amqp_conn])

   @app.route(["asgard/counts", "asgard/counts/errors"],
              type=RouteTypes.AMQP_RABBITMQ,
              vhost="fluentd")
   async def drain_handler(message):
       print(message)

Nesse exemplo, o handler ``drain_handler()`` recebe mensagens de ambas
as filas: ``asgard/counts`` e ``asgard/counts/errors``.

Se o handler lançar alguma exception, a mensagem é automaticamente
devolvida para a fila (reject com requeue=True); Se o handler rodar sem
erros, a mensagem é automaticamente confirmada (ack).


Lendo dados de um endpoint Server Side Events
---------------------------------------------

.. code:: python

   import json
   from asyncworker import App, RouteTypes, Options
   from asyncworker.connections import SSEConnection


   sse_conn = SSEConnection(url="http://172.18.0.31:8080/")
   app = App(connections=[sse_conn])

   @app.route(["/v2/events"], type=RouteTypes.SSE, options={Options.BULK_SIZE: 2})
   async def _on_event(events):
       event_names = [e.name for e in events]
       print(f"Events received: {len(events)} {event_names}")
       for event in events:
           data = ""
           if event.name == 'deployment_info':
               data = event.body['plan']['id']
           if event.name == 'deployment_success':
               data = event.body['id']
           if event.name == 'status_update_event':
               data = f"app={event.body['appId']}, task={event.body['taskId']} ({event.body['taskStatus']})"

           print(f"Event Received: {event.name} {data}")

Nesse exemplo, o handler ``_on_event()`` recebe os eventos enviados pelo
servidor. O objeto ``events`` é sempre uma lista, mesmo quando estamos
usando ``BULK_SIZE=1`` (Falaremos sobre isso mais a frente)


Recebendo dados através de requisições HTTP
-------------------------------------------

.. code:: python

   from aiohttp import web
   from asyncworker import App, RouteTypes

   # ...

   @app.route(routes=['/', '/hello'], methods=['GET'], type=RouteTypes.HTTP)
   async def index(request: web.Request) -> web.Response:
       return web.Response(body="Hello world")

Nesse exemplo, declaramos um handler ``index``, que receberá uma
instância de ``aiohttp.web.Request`` para cada acesso as rotas ``GET /``
e ``GET /hello``.


Rodando seu worker
------------------

Ambos os exemplos precisam de um ``main()`` para poderem rodar. Um
exemplo de ``main`` seria o seguinte, assumindo que o objeto ``app``
está no módulo ``myworker``:

.. code:: python


   from myworker import app

   app.run()

Nesse ponto sua app já estará rodando e caso você seja desconectado, um
loop ficará tentanto reconectar. A cada erro de conexão um log de
exception é gerado.