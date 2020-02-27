
[![Build Status](https://travis-ci.org/b2wdigital/async-worker.svg?branch=master)](https://travis-ci.org/b2wdigital/async-worker)
[![Test Coverage](https://api.codeclimate.com/v1/badges/887336d926f34f908b32/test_coverage)](https://codeclimate.com/github/b2wdigital/async-worker/test_coverage)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![PyPI version](https://badge.fury.io/py/async-worker.svg)](https://badge.fury.io/py/async-worker)


# O projeto

O projeto tem como objetivo ser um framework para escrever workers assíncronos em python. Por worker entende-se qualquer aplicação que rode por tempo indeterminado e que receba estímulos de várias origens diferentes. Essas orignes podem ser:

 - Uma mensagem em um broker, como RabbitMQ;
 - Um evento vindo se um servidor HTTP, como server side events;
 - Um evento recorrente gerado em um intervalo fixo de tempo;
 - Uma requisição HTTP
 - ...

 Documentação: https://b2wdigital.github.io/async-worker/


# Exemplos rápidos

Abaixo estão alguns exemplos bem simples que dão uma ideia do projeto e de como fica um código escrito com asyncorker.

## Handler HTTP

```python
from aiohttp import web

from asyncworker import App, RouteTypes

app = App()


@app.route(["/", "/other"], type=RouteTypes.HTTP, methods=["GET"])
async def handler(req: web.Request):
    return web.json_response({})


app.run()
```

Esse handler recebe reqisições HTTP (`GET`) nos seguintes endereços (por padrão): `http://127.0.0.1:8080/` e `http://127.0.0.1:8080/other`

## Handler RabbitMQ

```python
from typing import List

from asyncworker import App
from asyncworker.connections import AMQPConnection
from asyncworker.options import RouteTypes, Options
from asyncworker.rabbitmq import RabbitMQMessage

amqp_conn = AMQPConnection(
    hostname="127.0.0.1",
    username="guest",
    password="guest",
    prefetch_count=1024,
)

app = App(connections=[amqp_conn])


@app.route(
    ["queue", "queue-2"], type=RouteTypes.AMQP_RABBITMQ, options={Options.BULK_SIZE: 512}
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
