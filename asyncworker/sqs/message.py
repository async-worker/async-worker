from pydantic import BaseModel


class SQSMessage(BaseModel):
    body: str
    body_md5: str
    message_id: str
    receipt_handle: str

    @classmethod
    def parse(cls, data: dict):
        return cls(
            body=data["Body"],
            body_md5=data["MD5OfBody"],
            receipt_handle=data["ReceiptHandle"],
            message_id=data["MessageId"],
        )

    @property
    def body(self):
        return

    @property
    def deserialized_data(self):
        return self.body
