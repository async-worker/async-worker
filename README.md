
# Async Worker

## Propósito

Ser um microframework (inspirado no flask) para facilitar a escrita de workers de RabbitMQ.


## Exemplo

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


## Utils
### Timeit

Um gerenciador de contexto para marcar o tempo de execução de código e chamar
um callback `(str, float, Optional[Type[Exception]], Optional[Exception], Optional[traceback]) -> Coroutine` 
assíncrono ao final, com o tempo total de execução.

```python
import traceback
from typing import Type

from asyncworker.utils import Timeit


# App initialization stuff...

async def log_callback(name: str,
                       time_delta: float, 
                       exc_type: Type[Exception]=None, 
                       exc_val: Exception=None, 
                       exc_tb: traceback=None):
    log = {'name': name, 'time_delta': time_delta}
    if exc_type:
        await logger.error(log, exc_info=(exc_type, exc_val, exc_tb))
    else:
        await logger.info(log)


@app.route(["xablau-queue"], vhost="/")
async def drain_handler(message):
    async with Timeit(name="xablau-access-time", callback=log_callback):
        await access_some_remote_content()

```

Caso uma exceção seja levantada dentro do contexto, `log_callback` será chamado
com os dados da exceção.

Também é possível repassar keyword arguments para o callback:

```python
import traceback
from typing import Type

from asyncworker.utils import Timeit


# App initialization stuff...

async def log_callback(name: str,
                       time_delta: float, 
                       exc_type: Type[Exception]=None, 
                       exc_val: Exception=None, 
                       exc_tb: traceback=None,
                       dog: str=None):
    log = {'name': name, 'time_delta': time_delta, 'dog': dog}
    if exc_type:
        await logger.error(log, exc_info=(exc_type, exc_val, exc_tb))
    else:
        await logger.info(log)


@app.route(["xablau-queue"], vhost="/")
async def drain_handler(message):
    async with Timeit(name="xablau-access-time", callback=log_callback, dog='Xablau'):
        await access_some_remote_content()

```