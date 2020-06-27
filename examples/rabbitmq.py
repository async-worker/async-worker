from typing import List

from asyncworker import App
from asyncworker.connections import AMQPConnection
from asyncworker.options import RouteTypes, Options
from asyncworker.rabbitmq import RabbitMQMessage

amqp_conn = AMQPConnection(
    hostname="127.0.0.1", username="guest", password="guest", prefetch=1024
)

app = App(connections=[amqp_conn])


@app.route(
    ["queue"], type=RouteTypes.AMQP_RABBITMQ, options={Options.BULK_SIZE: 512}
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
