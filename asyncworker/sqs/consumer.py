import aiobotocore

from asyncworker.bucket import Bucket
from asyncworker.connections import SQSConnection
from asyncworker.sqs.message import SQSMessage

# 'add_permission'
# 'can_paginate'
# 'change_message_visibility'
# 'change_message_visibility_batch'
# 'close'
# 'create_queue'
# 'delete_message'
# 'delete_message_batch'
# 'delete_queue'
# 'get_paginator'
# 'get_queue_attributes'
# 'get_queue_url'
# 'get_waiter'
# 'list_dead_letter_source_queues'
# 'list_queue_tags'
# 'list_queues'
# 'meta'
# 'purge_queue'
# 'receive_message'
# 'remove_permission'
# 'send_message'
# 'send_message_batch'
# 'set_queue_attributes'
# 'tag_queue'
# 'untag_queue'


class SQSConsumer:
    def __init__(self, connection: SQSConnection, queue_url: str):
        self.connection = connection
        self.queue_url = queue_url
        self.session = aiobotocore.get_session()
        self._client = None
        # todo: replace const withconfig
        self._bucket = Bucket(size=10)

    def create_client_content(self):
        return self.session.create_client(
            "sqs",
            region_name=self.connection.region,
            aws_access_key_id=self.connection.access_key_id,
            aws_secret_access_key=self.connection.secret_access_key,
        )

    async def poll_queue(self):
        async with self.create_client_content() as client:
            self._client = client
            i = 0
            while True:
                i += 1
                # todo: MaxNumberOfMessages const to config
                response = await client.receive_message(
                    QueueUrl=self.queue_url, MaxNumberOfMessages=10
                )
                if "Messages" in response:
                    # todo: increment consumed_messages metric with inc(len(response['Messages']))
                    for message in response["Messages"]:
                        self._bucket.put(SQSMessage.parse(message))
                else:
                    # todo: increment metric
                    print("No messages found in queue", i)

    async def start(self):
        await self.poll_queue()
