Bem vindos à documentação oficial do projeto Asyncworker
========================================================

.. image:: https://github.com/async-worker/async-worker/actions/workflows/main.yaml/badge.svg?branch=main
.. image:: https://api.codeclimate.com/v1/badges/3119eaf8c7fee70af417/maintainability
.. image:: https://api.codeclimate.com/v1/badges/3119eaf8c7fee70af417/test_coverage

Introdução
----------

O projeto tem como objetivo ser um framework para escrever workers assíncronos em python. Por worker entende-se qualquer aplicação que rode por tempo indeterminado e que receba estímulos de várias origens diferentes. Essas origens podem ser:

- Uma mensagem em um broker, como RabbitMQ;
- Um evento recorrente gerado em um intervalo fixo de tempo;
- Uma requisição HTTP
- ...

O projeto está no Github: https://github.com/async-worker/async-worker

Abaixo você econtra mais detalhes sobre como tudo isso funciona.

.. toctree::
   :maxdepth: 1
   :titlesonly:

   incompat.rst
   versions.rst
   updateguide/index.rst
   userguide/index.rst
   devguide/index.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
