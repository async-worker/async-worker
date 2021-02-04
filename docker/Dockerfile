FROM python:3.8-alpine


WORKDIR /app
COPY . /app

RUN apk add --virtual .deps gcc g++ make openssl-dev libxml2 libffi-dev

RUN pip install async-worker

CMD ["python", "examples/metrics.py"]
