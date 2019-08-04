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
