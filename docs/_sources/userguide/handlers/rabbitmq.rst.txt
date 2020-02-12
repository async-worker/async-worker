RabbitMQ
========

Aqui você verá como escrever um handler que recebe mensagens de um broker RabbitMQ


Todo handler desse tipo recebe o mesmo parametro, que é uma lista de objetos :py:class:`asyncworker.rabbitmq.message.RabbitMQMessage`.


Isso significa que a assinatura dos seus handlers são fixas, ou seja, todos eles possuem essa assinatura:

.. code-block:: python

  from asyncworker.rabbitmq.message import RabbitMQMessage
  from typing import List

  async def handler(msgs: List[RabbitMQMessage]):
    ...


Como no caso de handlers RabitMQ é preciso ter uma conexão prévia com o servidor d e filas, precisamos criar uma instância de :py:class:`asyncworker.connections.AMQPConnection`. Essa instância deve ser passada no momento da criação de sua :ref:`Asyncworker App <asyncworker-app>`.

Essa instância de conexão pode também ser usada dentro do handler, caso necessário.


Um exemplo disso é quando precisamos de um handler que lê mensagens de um fila e publica em outra. Esse exemplo pode ser escrito assim:

.. code-block:: python

  from typing import List

  from asyncworker import App
  from asyncworker.connections import AMQPConnection
  from asyncworker.options import RouteTypes
  from asyncworker.rabbitmq import RabbitMQMessage

  amqp_conn = AMQPConnection(
                hostname="127.0.0.1",
                username="guest",
                password="guest",
                prefetch_count=256
              )

  app = App(connections=[amqp_conn])


  @app.route(["original_queue"], type=RouteTypes.AMQP_RABBITMQ)
  async def handler(messages: List[RabbitMQMessage]):
      await amqp_conn.put(
          data={"dogs": ["Xablau", "Xena"]},
          exchange="ANOTHER_EXCHANGE",
          routing_key="another-routing-key"
      )


se a fila de destino estiver um outro virtual host, basta pegar uma nova conexão com esse virtual host acessando o atributo (dict like) com o nome do virtual host desejado, no objeto da conexão, assim:

.. code-block:: python


  @app.route(["original_queue"], type=RouteTypes.AMQP_RABBITMQ)
  async def handler(messages: List[RabbitMQMessage]):
      await amqp_conn["other-vhost"].put(
          data={"dogs": ["Xablau", "Xena"]},
          exchange="ANOTHER_EXCHANGE",
          routing_key="another-routing-key"
      )

Parametros adicionais para o decorator route()
----------------------------------------------

Para um handler RabbitMQ o decortor ``route()`` pode receber alguns parametros adicionais.

  - Lista de filas de onde esse handler receberá mensagens
  - ``type=RouteTypes.AMQP_RABBITMQ``
  - ``vhost``: Indica em qual vhost as filas estatão definidas. Se não passarmos nada será usado ``vhost="/"``
  - ``options`` pode ser um dicionário compatível com o modelo `asyncworker.routes._AMQPRouteOptions <https://github.com/b2wdigital/async-worker/blob/691549d296f7dc2f8dfc0c58452ccd1f88375847/asyncworker/routes.py#L119-L124>`_.

Exemplo de valores para o campo options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

o dicionário ``options`` pode ter as seguintes chaves:

  - :py:attr:`Options.BULK_SIZE <asyncworker.options.Options.BULK_SIZE>`: Esse valor é um inteiro e diz qual será o tamanho máximo da lista que o handler vai receber, a cada vez que for chamado.
  - :py:attr:`Options.BULK_FLUSH_INTERVAL <asyncworker.options.Options.BULK_FLUSH_INTERVAL>`: Inteiro e diz o tempo máximo que o bulk de mensagens poderá ficar com tamanho menor do que ``bulk_size``. Exemplo: Se seu handler tem um bulk_size de 4096 mensagens mas você recebe apenas 100 msg/min na fila em alguns momentos seu handler será chamado recebendo uma lista de mensagens **menor** do que 4096.
  - :py:attr:`Events.ON_SUCCESS <asyncworker.options.Events.ON_SUCCESS>`: Diz qual será a ação tomada pelo asyncworker quando uma chamada a um handler for concluída com sucesso, ou seja, o handler não lançar nenhuma exception. O Valor padrão é :py:attr:`Actions.ACK <asyncworker.options.Actions.ACK>`
  - :py:attr:`Events.ON_EXCEPTION <asyncworker.options.Events.ON_EXCEPTION>`: Diz qual será a ação padrão quando a chamada a um handler lançar uma excação não tratada. O valor padrão é :py:attr:`Actions.REQUEUE <asyncworker.options.Actions.REQUEUE>`


Exemplo de um código que usa essas opções:

.. code-block:: python

  from asyncworker import App
  from asyncworker.options import Options, Actions, Events

  @app.route(
      ["queue"],
      options={
          Options.BULK_SIZE: 1000,
          Options.BULK_FLUSH_INTERVAL: 60,
          Events.ON_SUCCESS: Actions.ACK,
          Events.ON_EXCEPTION: Actions.REJECT,
      },
  )
  async def _handler(messages):
      pass


Uma nota sobre bulk_size e prefetch
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

O valor do ``BULK_SIZE`` sempre é escolhido com a fórmula: ``min(BULK_SIZE, PREFRETCH)``. Isso para evitar que o código fique em um deadlock, onde ao mesmo tempo que ele aguarda o bulk encher para poder pegar mais mensagens da fila, ele está aguardando o bulk esvaziar para pegar mais mensagens da fila.


Flush timeout
~~~~~~~~~~~~~~~

Com o flush timeout a ``app`` não necessita ficar presa esperando o bucket encher para conseguir processar as mensagens.
Após o tempo do ``FLUSH_TIMEOUT`` (que são :py:attr:`DefaultValues.BULK_FLUSH_INTERVAL <asyncworker.options.DefaultValues.BULK_FLUSH_INTERVAL>` segundos por default) a ``app`` irá enviar todas as mensagens que já possui para o ``_handler``.
Por exemplo, se tivermos um ``handler`` que possui:

 - Um ``BULK_SIZE`` de 1.000
 - As mensagens para esse handles são publicadas diariamente
 - E o bucket desse handler ficou com 500 mensagens

Nesse caso a ``app`` irá esperar o timeout do flush para liberar essas mensagens para o ``handler``.

Caso queria alterar o tempo default do timeout do flush basta definir env ``ASYNCWORKER_FLUSH_TIMEOUT`` com um número que representará os segundos em que a app irá esperar para realizar o flush



Exemplo de um código mais completo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

  from typing import List
  from asyncworker import App, RouteTypes
  from asyncworker.connections import AMQPConnection
  from asyncworker.rabbitmq.message import RabbitMQMessage


  amqp_conn = AMQPConnection(
                host="127.0.0.1",
                user="guest",
                password="guest",
                prefetch_count=256
              )

  app = App(connections=[amqp_conn])

  @app.route(["asgard/counts", "asgard/counts/errors"],
             type=RouteTypes.AMQP_RABBITMQ,
             vhost="fluentd")
  async def drain_handler(messages: List[RabbitMQMessage]):
      for m in messages:
        print(m)


Nesse exemplo, o handler ``drain_handler()`` recebe mensagens de ambas as filas: ``asgard/counts`` e ``asgard/counts/errors``.

Se o handler lançar alguma exception, a mensagem é automaticamente devolvida para a fila (reject com requeue=True);
Se o handler rodar sem erros, a mensagem é automaticamente confirmada (ack).



Escolhendo, individualmente, qual ação será dada a cada mensgem recebida
-------------------------------------------------------------------------

Existem situações onde você precisa que algumas as mensagens recebidas pelo handler teham tratamentos **diferentes** das outras mensagens. Ou seja, nem sempre você quer que todas recebam ``ack`` ou ``requeue``.

Para isso o objeto recebido por um handler (:py:class:`RabbitMQMessage <asyncworker.rabbitmq.message.RabbitMQMessage>`) possui alguns métodos:

.. autoclass:: asyncworker.rabbitmq.message.RabbitMQMessage
  :noindex:
  :members: reject, accept


Opcionalmente, caso seja necessário rejeitar uma mensagem e ao mesmo tempo **não** devolver essa mensagem pra fila,
podemos chamar ``message.reject(requeue=False)``. O valor default do ``requeue`` é ``True``.


Sobre AMQPConnection
---------------------

Esse objeto é o ponto de comunicação principal com um broker RabbitMQ. Aqui temos um método ``put`` onde podemos enviar novas mensagens ao broker.

Essa classe é um modelo pydantic e pode receber alguns parametros no construtor. Esses parametros estão na declaração dessa classe. :py:class:`asyncworker.connections.AMQPConnection`.
