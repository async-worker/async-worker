# EasyQueue

An easy way to asynchronously handle AMQP queue consumption.

# Installation

`pip install easyqueue` 

# Run tests

*Simple test run:*  
`py.test`

*Show coverage*  
`py.test --cov=easyqueue`

# AsyncQueue

Class used for asynchronously connecting and consuming
 `amqp` queues. `AsyncQueue` uses the delegation pattern
 to provide abstractions for queue communication.

 ## Hello World - the simplest code that does something

``` python
import asyncio
from easyqueue.async import AsyncQueue, AsyncQueueConsumerDelegate


class MyConsumer(AsyncQueueConsumerDelegate):
    queue_name = 'awesome_queue_name'
    
    def __init__(self, loop: asyncio.AbstractEventLoop, queue: AsyncQueue):
        self.loop = loop
        self.queue = queue
        
    async def on_before_start_consumption(self, queue_name: str, queue: AsyncQueue):
        print("I'm called when queue consumption starts !")
        
    async def on_message_handle_error(
        print("I'm called if an unhandled exception is raised on" 
              "on_queue_message or on_queue_error")

    async def on_queue_message(self, content: dict, delivery_tag: str, queue: AsyncQueue):
        """
        Called every time that a new, valid and deserialized message
        is ready to be handled.
        """
        print(content)
        await self.queue.ack(delivery_tag)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    queue = AsyncQueue(
        host='localhost',
        username='guest',
        password='guest',
        delegate_class=MyConsumer,
        loop=loop
    )

    loop.create_task(queue.start_consumer())
    loop.run_forever()

```

# AsyncQueueConsumerDelegate Protocol

## `on_queue_message`

## `on_queue_error`

## `on_before_start_consumption`

## `on_message_handle_error`

##  `on_connection_error`

