Atualizando sua App Asyncworker
===============================


0.5.x -> 0.6.0
---------------

Nessa versão, tornamos obrigatório o uso do Enum ``RouteTypes`` e a
assinatura de ``app.route`` mudou. Ex.:

.. code-block:: python

  from asyncworker.models import RouteTypes

  @app.route(['/sse'], type=RouteTypes.SSE)
  async def event_handler(events):
      pass


0.1.x -> 0.2.0
--------------

Na versão ``0.2.0`` criamos a possibilidade de receber mensagens em lote. E a partir dessa versão a assinatura do handler mudo para:

.. code-block:: python

  from asyncworker.rabbitmq.message import RabbitMQMessage

  async def handler(messages: List[RabbitMQMessage]):
    pass

As instâncias do objeto ``asyncworker.rabbitmq.RabbitMQMessage`` já vêm por padrão configurado para receber ``ack()`` depois que o handler retornar (sem exception), mas o handler pode mudar isso chamando o método ``message.reject()`` para cada mensagem que precisar ser devolvida para a fila.

O conteúdo da mensagem original está agora no atributo ``message.body``. Então um handler antigo que era assim:

.. code-block:: python

  from asyncworker import App

  app = App(host="127.0.0.1", user="guest", password="guest", prefetch_count=256)

  @app.route(["asgard/counts", "asgard/counts/errors"], vhost="fluentd")
  async def drain_handler(message):
      logger.info(message)


passa a ser assim:

.. code-block:: python

  om asyncworker import App

  app = App(host="127.0.0.1", user="guest", password="guest", prefetch_count=256)

  @app.route(["asgard/counts", "asgard/counts/errors"], vhost="fluentd")
  async def drain_handler(messages):
      for m in messages:
        logger.info(message.body)
