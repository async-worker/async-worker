Como fechar uma nova versão do async-worker
===========================================

Todas as release do async-worker são feitas através da `feature de Release do Github <https://docs.github.com/en/github/administering-a-repository/managing-releases-in-a-repository>`_. Mas existem alguns passos que ainda são manuais no processo de preparar o código para podermos publicar uma nova release.


Algumas preparações se aplicam a todas as versões, são elas:

- Fazer o ajuste da versão no código. A string da versão fica no arquivo ``setup.py``, na raiz do projeto. Essa string é importante pois é o valor que será usado no momento de publicar o pacote do async-worker no `Pypi <https://pypi.org/project/async-worker/>`_.

- Gerar a documentação mais atual do projeto. Isso é necessário pois, em geral, cada PR que é mergeado traz sua documentação nos arquivos ``.rst`` que ficam na pasta ``docs-src/``. Mas esse é apenas o código-fonte da documentação. E a versão HTML, que é servida pelo `Github Pages <https://pages.github.com/>`_, fica em ``docs/*``.

Para gerar uma nova versão da documentação basta executar, na raiz do projeto: ``pipenv run make-docs`` e comitar o resultado.

Publicando uma minor release
-----------------------------

Para uma versão retro-compatível, após fazer os passos acima (que são comuns a todas as versões) basta ir até a página de `releases do projeto <https://github.com/async-worker/async-worker/releases>`_ e publicar o Draft que já estará lá preparado.

Temos apenas que lembrar de remover a linha que diz: "Como atualizar para". Precisamos fazer isso pois como essa é uma release retro-compatível não há documentação de "como migrar" pois nenhum passo é necessário.

Publicando uma Major release
-----------------------------

Para uma versão retro-incompatível, além de fazer os passos acima (que são comuns a todas as versões) é preciso escrever o guia de migração documentanto qual breaking change essa nova major version está trazendo e o que é necessário alterar no código de um projeto para que seja possível usar essa nova versão.

Essa documentação deve ficar dentro da pasta ``docs-src/updateguide/`` e deve ser um novo arquivo ``.rst`` que leva o nome da nova versão. Um exemplo para a versão ``0.19.0``, a documentação de migração está no arquivo ``docs-src/updateguide/v0.19.0.rst``.

Depois basta ir até a página de `releases do projeto <https://github.com/async-worker/async-worker/releases>`_ e publicar o Draft que já estará lá preparado.
