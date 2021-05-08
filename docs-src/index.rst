Bem vindos à documentação oficial do projeto Asyncworker
========================================================


O projeto tem como objetivo ser um framework para escrever workers assíncronos em python. Por worker entende-se qualquer aplicação que rode por tempo indeterminado e que receba estímulos de várias origens diferentes. Essas origens podem ser:

 - Uma mensagem em um broker, como RabbitMQ;
 - Um evento recorrente gerado em um intervalo fixo de tempo;
 - Uma requisição HTTP
 - ...

O projeto está no Github: https://github.com/async-worker/async-worker

 .. image:: https://github.com/async-worker/async-worker/actions/workflows/main.yaml/badge.svg?branch=main
 .. image:: https://api.codeclimate.com/v1/badges/887336d926f34f908b32/maintainability
 .. image:: https://api.codeclimate.com/v1/badges/3119eaf8c7fee70af417/test_coverage

Abaixo você econtra mais detalhes sobre como tudo isso funciona.

.. toctree::
   :maxdepth: 3
   :titlesonly:

   incompat.rst
   versions.rst
   update.rst
   userguide/index.rst
   devguide/index.rst
   changelog/index.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
