
[![Build Status](https://github.com/async-worker/async-worker/actions/workflows/main.yaml/badge.svg?branch=main)](https://github.com/async-worker/async-worker/actions/workflows/main.yaml)
[![Test Coverage](https://api.codeclimate.com/v1/badges/3119eaf8c7fee70af417/test_coverage)](https://codeclimate.com/github/async-worker/async-worker/test_coverage)
[![Maintainability](https://api.codeclimate.com/v1/badges/3119eaf8c7fee70af417/maintainability)](https://codeclimate.com/github/async-worker/async-worker/maintainability)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![PyPI version](https://badge.fury.io/py/async-worker.svg)](https://badge.fury.io/py/async-worker)


![Logo](./logo.png)

# async-worker

O projeto tem como objetivo ser um framework para escrever workers assíncronos em python. Por worker entende-se qualquer aplicação que rode por tempo indeterminado e que receba estímulos de várias origens diferentes. Essas orignes podem ser:

 - Uma mensagem em um broker, como RabbitMQ;
 - Um evento recorrente gerado em um intervalo fixo de tempo;
 - Uma requisição HTTP
 - ...

 Documentação: https://async-worker.github.io/async-worker/

# Exemplos rápidos

Abaixo estão alguns exemplos bem simples que dão uma ideia do projeto e de como fica um código escrito com async-worker.

## Handler HTTP

```python
from aiohttp import web

from asyncworker import App

app = App()


@app.http.get(["/", "/other"])
async def handler():
    return web.json_response({})


app.run()
```

Esse handler recebe reqisições HTTP (`GET`) nos seguintes endereços (por padrão): `http://127.0.0.1:8080/` e `http://127.0.0.1:8080/other`

## Handler RabbitMQ

```python
from typing import List

from asyncworker import App
from asyncworker.connections import AMQPConnection
from asyncworker.options import Options
from asyncworker.rabbitmq import RabbitMQMessage, AMQPRouteOptions

amqp_conn = AMQPConnection(
    hostname="127.0.0.1",
    username="guest",
    password="guest",
    prefetch_count=1024,
)

app = App(connections=[amqp_conn])


@app.amqp.consume(
    ["queue", "queue-2"], options=AMQPRouteOptions(bulk_size=512)
)
async def handler(messages: List[RabbitMQMessage]):
    print(f"Received {len(messages)} messages")
    for m in messages:
        await amqp_conn.put(
            data=m.body, exchange="other", routing_key="another-routing-key"
        )


@app.run_every(1)
async def produce(app: App):
    await amqp_conn.put(data={"msg": "ok"}, routing_key="queue")


app.run()
```

Esse handler recebe mensagens das filas `queue` e `queue-2` em lotes de 512 mensagens. Se essas duas filas demorarem mais de 60 segundos para acumular, juntas, 1024 mensagens o handler será chamado imediatamente com a quantidade de mensagens que estiver disponível no momento.

O que esse handler está fazendo é apenas pegar todas as mensagens que ele recebe e enviar para o `exchange="", routing_key="queue"`.

---

Logo created with [DesignEvo logo maker](https://www.designevo.com/)
