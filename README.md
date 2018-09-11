
[![Build Status](https://travis-ci.org/B2W-BIT/async-worker.svg?branch=master)](https://travis-ci.org/B2W-BIT/async-worker)
[![codecov](https://codecov.io/gh/B2W-BIT/async-worker/branch/master/graph/badge.svg)](https://codecov.io/gh/B2W-BIT/async-worker)

# Async Worker

## Propósito

Ser um microframework (inspirado no flask) para facilitar a escrita de workers assíncronos.
Atualmente o projeto suporta as seguintes backends:

* [RabbitMQ](https://www.rabbitmq.com/): Somente leitura de mensagens. A implementação de publicação de mensagens será feita no #9;
* [Server Side Events](https://en.wikipedia.org/wiki/Server-sent_events): Possibilidade de eventos de um endpoint que emite implementa Server Side Events.


## Exemplos

### Worker lendo dados de um RabbitMQ

```python

from asyncworker import App

app = App(host="127.0.0.1", user="guest", password="guest", prefetch_count=256)

@app.route(["asgard/counts", "asgard/counts/errors"], vhost="fluentd")
async def drain_handler(message):
    logger.info(message)

```

Nesse exemplo, o handler `drain_handler()` recebe mensagens de ambas as filas: `asgard/counts` e `asgard/counts/errors`.

Se o handler lançar alguma exception, a mensagem é automaticamente devolvida para a fila (reject com requeue=True);
Se o handler rodar sem erros, a mensagem é automaticamente confirmada (ack).

### Worker lendo dados de um endpoint Server Side Events

```python

from asyncworker.sse.app import SSEApplication
import logging

app = SSEApplication(url="http://172.18.0.31:8080/", logger=logging.getLogger())

@app.route(["/v2/events"], options={Options.BULK_SIZE: 2})
async def _on_event(events):
    import json
    event_names = [e.name for e in events]
    print(f"Events received: {len(events)} {event_names}")
    for event in events:
        data = ""
        if event.name == 'deployment_info':
            data = event.body['plan']['id']
        if event.name == 'deployment_success':
            data = event.body['id']
        if event.name == 'status_update_event':
            data = f"app={event.body['appId']}, task={event.body['taskId']} ({event.body['taskStatus']})"

        print(f"Event Received: {event.name} {data}")
```

Nesse exemplo, o handler `_on_event()` recebe os eventos enviados pelo servidor. O objeto `events` é sempre uma lista, mesmo quando estamos usando `BULK_SIZE=1` (Falaremos sobre isso mais a frente)

### Rodando esses código

Ambos os exemplos precisam de um `main()` para poderem rodar. Um exemplo de `main` seria o seguinte, assumindo que o objeto `app` está no módulo `myworker`:

```python

from myworker import app

app.run()

```

Nesse ponto sua app já estará rodando e caso você seja desconectado, um loop ficará tentanto reconectar. A cada erro de conexão um log de exception é gerado.

A seguir temos documentações específicas sobre cada backend implementado


# RabbitMQ

## Rejeitando uma mensagem e não colocando-a de volta na fila

Opcionalmente, caso seja necessário rejeitar uma mensagem e ao mesmo tempo **não** devolver essa mensagem pra fila,
podemos chamar `message.reject(requeue=False)`. O valor default do `requeue` é `True`.

## Configurações de ação padrão em caso de sucesso e exception

É possível escolher o que o asynworker fará com as mensagens em caso de sucesso (handler executa sem lançar exceção)
ou em caso de falha (handler lança uma exception não tratada).

As opções são: Events.ON_SUCCESS e Events.ON_EXCEPTION. Ambas são passadas a cada rota de consumo registrada, ex:

```python
from asynworker.options import Events, Actions

@app.route(["queue1", "queue2"], options={
                                  Events.ON_SUCCESS: Actions.ACK,
                                  Events.ON_EXCEPTION: Actions.REJECT,
                                  })
async def handler(messages):
    ...
```

Nesse caso, se o handler rodar com sucesso, todas as mensagem soferão `ACK`. Caso uma exceção não tratada seja capturada
pelo asyncworker todas as mensagens sofrerão `REJECT`.

### Opções possíveis

 - `Actions.ACK`: Confirma a mensagem para o RabbitMQ
 - `Actions.REJECT`: Rejeita a mensagem e **não devolve para a fila de origem**
 - `Actions.REQUEUE`: Rejeita a mensagem e **devolve** para a fila de origem.

### Sobrescrevendo a ação padrão apenas para algumas mensagens

É possível escolher uma ação diferente da padrão para qualquer mensagem do bulk que foi entregue ao handler. Para isso
basta chamar um dos métodos do objeto `RabbitMQMessage`. São eles:

 - `.accept()`: Marca a mensagem para ser confirmada para o RabbitMQ
 - `.reject(requeue=False)`: Marca a mensagem para ser rejeitada e **não devolvida** para a fila de origem
 - `.reject(requeue=True)`: Marca a mensagem para ser rejeitada e **devolvida** para a fila de origem

O valor default para o `.reject()` é `requeue=True`.

# Server Side Events 


# Recebendo dados em lote

o async-worker permite que você receba seus dados em lotes de tamanho definido por você. A forma de escolher esse lote é atrávez da opção `Options.BULK_SIZE`.
Essa opção é passada para cada um dos handlers, individualmente. O default é `BULK_SIZE=1`.

## Escolhendo o tamanho do BULK que será usado

Assumindo que nossa `app` já está criada. Independente de qual tipo de app é, o decorator `@app.route()` recebe um kwarg chamado `options` onde podemos passar o BULK_SIZE, assim:

```python
from asyncworker.options import Options

@app.route(..., options={Options.BULK_SIZE: 1000})
async def _handler(dat):
    for m in messages:
      logger.info(message.body)

```

Nesse exemplo, o `_handler` só será chamado quando o async-worker tiver, **já nas mãos**, 1000 itens. Os 1000 itens serão passados de uma única vez para o handler, em uma lista.

### BULK_SIZE e o backend RabbitMQ

O valor do BULK_SIZE sempre é escolhido com a fórmula: `min(BULK_SIZE, PREFRETCH)`. Isso para evitar que o código fique em um deadlock, onde ao mesmo tempo que ele aguarda o bulk encher para poder pegar mais mensagens da fila, ele está aguardando o bulk esvaziar para pegar mais mensagens da fila.
 
## Atualizando o async-worker no seu projeto

### 0.1.x > 0.2.0

Na versão `0.2.0` criamos a possibilidade de receber mensagens em lote. E a partir dessa versão
a assinatura do handler mudo para:

```python
from asyncworker.rabbitmq.message import Message

async def handler(messages: List[Message]):
  pass
```

As instâncias do objeto `asyncworker.rabbitmq.RabbitMQMessage` já vêm por padrão configurado para receber `ack()` 
depois queo handler retornar (sem exception), mas o handler pode mudar isso
chamando o método `message.reject()` para cada mensagem que precisar ser devolvida para a fila.

O conteúdo da mensagem original está agora no atributo `message.body`. Então um handler antigo que era assim:

```python
from asyncworker import App

app = App(host="127.0.0.1", user="guest", password="guest", prefetch_count=256)

@app.route(["asgard/counts", "asgard/counts/errors"], vhost="fluentd")
async def drain_handler(message):
    logger.info(message)

```

passa a ser assim:

```python
from asyncworker import App

app = App(host="127.0.0.1", user="guest", password="guest", prefetch_count=256)

@app.route(["asgard/counts", "asgard/counts/errors"], vhost="fluentd")
async def drain_handler(messages):
    for m in messages:
      logger.info(message.body)

```

## Utils
### Timeit (0.3.0+)

#### Gerenciador de contexto

Um gerenciador de contexto para marcar o tempo de execução de código e chamar
um callback `Callable[..., Coroutine]` 
assíncrono ao final, com o tempo total de execução.

```python
import asyncio
from asyncworker.utils import Timeit


async def log_callback(**kwargs):
    print(kwargs)
    # >>> {'transactions': {'xablau': 1.0028090476989746}, 'exc_type': None, 'exc_val': None, 'exc_tb': None}


async def main():
    async with Timeit(name="xablau", callback=log_callback):
        await asyncio.sleep(1)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```

Caso uma exceção seja levantada dentro do contexto, `log_callback` será chamado
com os dados da exceção explicitamente.


```python
import asyncio
from asyncworker.utils import Timeit


async def log_callback(**kwargs):
    print(kwargs)
    # >>> {'transactions': {'xablau': 3.0994415283203125e-06}, 'exc_type': <class 'KeyError'>, 'exc_val': KeyError('error',), 'exc_tb': <traceback object at 0x10c10c7c8>}


async def main():
    async with Timeit(name="xablau", callback=log_callback):
        raise KeyError("error")
        
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```

#### Decorator

Também é possível utilizar `Timeit` como um decorator:

```python
# ...

@app.route(["xablau-queue"], vhost="/")
@Timeit(name="xablau-access-time", callback=log_callback)
async def drain_handler(message):
    await access_some_remote_content()
```

#### Múltiplas transações (0.4.0+)

Muitas vezes queremos ter várias métricas ao mesmo tempo para contar o tempo
dentro de um mesmo contexto de execução. Para isso, uma mesma instância pode
receber múltiplas chamadas.

```python
async def printit(**kwargs):
    print(kwargs)
    # >>> {'transactions': {'c': 0.10274815559387207, 'b': 0.20585179328918457, 'a': 0.3061490058898926}, 'exc_type': None, 'exc_val': None, 'exc_tb': None}


async def foo():
    async with Timeit(name='a', callback=printit) as timeit:
        await asyncio.sleep(.1)
        async with timeit(name='b'):
            await asyncio.sleep(.1)
            async with timeit(name='c'):
                await asyncio.sleep(.1)
```
