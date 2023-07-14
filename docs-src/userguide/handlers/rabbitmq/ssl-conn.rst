Conectando a um Broker usando SSL
----------------------------------

.. versionadded:: 0.20.2

Para que possamos conectar em um Broker usando ssl precisamos criar um `SSLContext` e passar esse objeto para o nosso objeto :py:class:`AMQPConnection <asyncworker.connections.AMQPConnection>`.

Esse contexto é criado usando o módulo `ssl <https://docs.python.org/3/library/ssl.html>`_ da stdlib do Python mesmo. Uma forma simples de criar um contexto é usar:

.. code-block:: python


   import ssl

   ctx = ssl.create_default_context()


Esse contexto deve ser passado ao Objeto :py:class:`AMQPConnection <asyncworker.connections.AMQPConnection>`, dessa forma:


.. code-block:: python

    from asyncworker import App
    from asyncworker.connections import AMQPConnection
    import ssl


    amqp_conn = AMQPConnection(host="127.0.0.1",
                  user="guest",
                  password="guest",
                  prefetch_count=256,
                  ssl=ssl.create_default_context()
                )
    app = App(connections=[amqp_conn])

    @app.amqp.consume(["asgard/counts", "asgard/counts/errors"],
               vhost="fluentd")
    async def drain_handler(message):
        print(message)


Esse código consegue se conectar a um broker que usa ssl. Nesse caso o asyncworker vai conferir so certificados do servidor. Caso você esteja se conectando a um broker com certificados auto-assinados, você poderá passar o parametro ``verify_ssl=False`` para o objeto :py:class:`AMQPConnection <asyncworker.connections.AMQPConnection>`.


.. code-block:: python

    from asyncworker import App
    from asyncworker.connections import AMQPConnection
    import ssl


    amqp_conn = AMQPConnection(host="127.0.0.1",
                  user="guest",
                  password="guest",
                  prefetch_count=256,
                  ssl=ssl.create_default_context(),
                  verify_ssl=False
                )
    app = App(connections=[amqp_conn])
