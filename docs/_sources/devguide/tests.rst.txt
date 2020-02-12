Escrevendo Testes Unitários
===========================


Por causa :ref:`da incompatibilidade com múltiplos loops <incompat>` para escrever testes você precisa ter certeza que seu test runner não está criando novos loops para cada um dos casos de teste sendo rodados. Por padrão o `asynctest <https://github.com/Martiusweb/asynctest>`_ faz isso. No caso do asynctest, basta adicionar um atributo ``use_default_loop = True`` (doc `aqui <https://asynctest.readthedocs.io/en/latest/asynctest.case.html#asynctest.TestCase.use_default_loop>`_) em sua classe de teste.
