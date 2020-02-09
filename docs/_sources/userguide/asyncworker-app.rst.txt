.. _asyncworker-app:

Sobre a classe principal App
============================

Todo código do asyncworker começa com uma instância de :py:class:`asyncworker.app.App`. Esse é o objeto onde declaramos as "rotas" da sua aplicação e é também onde chamamos o método ``run()``, que é quem efetivamente dá boot em nossa aplicação.

Criando uma nova App
--------------------

O objeto App recebe em seu construtor uma lista de conexões. As conexões são a forma de dizer ao asyncowker como falar com as origens dos estímulos. São esses estímulos que farão com que seus handler sejam executados.

As conexões possíveis estão mo módulo :py:mod:`asyncworker.connections`.

As instâncias dessas conexões podem ser usadas dentro do handlers, se necessário.


Definindo handlers em sua App Asyncworker
-----------------------------------------


Nesse objeto temos um método especial chamado ``route()``. Esse método é o ponto central para registrar seus handlers. Esse mesmo método registra handlers de todos os tipos, por isso recebe um parametro para saber qual origem de estímulos fará esse handler ser chamado.

Os tipos estão definidos no Enum :py:class:`asyncworker.options.RouteTypes`.


Esse método tem a seguinte assinatura:


.. automethod:: asyncworker.app.App.route
  :noindex:

O primeiro parâmetro tem múltiplos significados, dependento do tipo de handler que você está registrando.

Por exmeplo, para um handler HTTP essa lista é lista de paths do Request HTTP que farão esse handler ser chamado. Se for um handlar RabbitMQ essa lista representa a lista de filas que esse handler estará "conectado", ou seja, a cada mensagem depositada em quaisquer uma dessas filas, esse handler será chamado.

Um outro parametro obrigatório é o parametro ``type``. Ele, necessariamente, deve ser uma das opções do Enum :py:class:`asyncworker.options.RouteTypes`.

Esse método deve ser usado como um decorator em funções que serão registradas como handlers da sua App.
