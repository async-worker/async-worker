.. _versioning:

Compatibilidade de Versões do asyncworker
==========================================

O versionamento do projeto segue a mesma linha do `Semver <https://semver.org/>`_ mas com uma peculiaridade. Como esse é um projeto que ainda está em pleno desenvolvimento ainda falta um longo caminho até chegarmos a uma versão ``1.0``.

Por isso, o que fazemos é o seguinte: Mudamos apenas os valores da ``MINOR`` e ``PATCH``.

Quando mudamos apenas a ``PATCH`` version significa que o código novo é retro-compatível com o antigo, ou seja, pode ser atualizado sem problemas. Sem precisar olhar changelogs.

Quando mudamos a ``MINOR`` version significa que o changelog requer atenção. Seja um mudança simples ou uma mudança mais complexa que vai demandar ajustes no seu código. É recomendado que você olhe :ref:`as instruções de atualização <updateguide>` para saber se você precisa ajustar alguma coisa.

Lembrando que a formação da versão é ``0.MINOR.PATCH``.


Versões do Python suportadas
---------------------------

O projeto asyncworker suporta sempre as versões ativas do Python. Por suporte entende-se que testes são rodados nessa versão e para que um Pull Request possa ser mergeado os testes devem passar nas versões suportadas do python.

Seguimos esse calendário para escolher quais versões do Python são ativamente testadas no projeto: https://endoflife.date/python

Atualização de dependências
---------------------------

O asyncworker depende basicamente de dois outros projetos:

- `aiohttp <https://docs.aiohttp.org/en/stable/>`_
- `Pydantic <https://pydantic-docs.helpmanual.io/>`_

Sempre uma versão do Python deixar de ser suportada pelo asyncworker ou quaisquer das dependências principais precisar ser atualizadas isso será considerado uma mudança (potencialmente) retro-incompatível e por isso o asyncworker terá sua minor version aumentada.
