Bem vindos à documentação oficial do projeto Asyncworker
========================================================


O projeto tem como objetivo ser um framework para escrever workers assíncronos em python. Por worker entende-se qualquer aplicação que rode por tempo indeterminado e que receba estímulos de várias origens diferentes. Essas orignes podem ser:

 - Uma mensagem em um broker, como RabbitMQ;
 - Um evento vindo se um servidor HTTP, como server side events;
 - Um evento recorrente gerado em um intervalo fixo de tempo;
 - Uma requisição HTTP
 - ...

 Abaixo você econtra a documentação do projeto.

.. toctree::
   :maxdepth: 3
   :titlesonly:

   intro.rst
   incompat.rst
   userguide/index.rst
   devguide/index.rst
   changelog/index.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
