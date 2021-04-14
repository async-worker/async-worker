import asyncio

from aiologger import Logger

from aiohttp import web, ClientSession

from asyncworker import App
from asyncworker.http.decorators import parse_path
from asyncworker.http.wrapper import RequestWrapper
from asyncworker.metrics import Counter, Gauge


app = App()
logger = Logger.with_default_handlers()

c = Counter("count", "Contagem")
g = Gauge("duration", "Duration")
g_label = Gauge("with_label", "Gauge with label", labelnames=["label"])

REQUESTS = [
    ("http://asyncworker:8080/count", 1000),
    ("http://asyncworker:8080/metrics", 1000),
    ("http://asyncworker:8080/gauge-with-label/A", 1000),
    ("http://asyncworker:8080/gauge-with-label/B", 1000),
    ("http://asyncworker:8080/sleep/1", 10),
    ("http://asyncworker:8080/sleep/5", 10),
]
REQUESTS_INTERVAL_IN_SECONDS = 15


@app.http.get(["/count"])
async def handler():
    c.inc()
    return web.json_response({})


@app.http.get(["/sleep/{duration}"])
@parse_path
async def by_id(duration: int):
    with g.time():
        await asyncio.sleep(duration)
    return web.json_response({})


@app.http.get(["/gauge-with-label/{label}"])
@parse_path
async def one_param(label: str):
    with g_label.labels(label=label).track_inprogress():
        pass
    return web.json_response({})


@app.run_on_startup
async def startup(app):
    app["client_session"] = ClientSession()
    print("app started")


@app.run_on_shutdown
async def shutdown(app):
    await app["client_session"].close()


@app.run_every(seconds=REQUESTS_INTERVAL_IN_SECONDS)
async def make_requests(app):
    session: ClientSession = app["client_session"]

    async def do_get(url: str):
        async with session.get(url) as response:
            await response.read()

    await logger.info(f"Generating requests.")

    for (url, number_of_requests) in REQUESTS:
        for _ in range(number_of_requests):
            asyncio.create_task(do_get(url))


app.run()
