from aiohttp import web

from asyncworker import App, RouteTypes
from asyncworker.http.decorators import parse_path
from asyncworker.http.wrapper import RequestWrapper

app = App()


@app.route(["/", "/other"], type=RouteTypes.HTTP, methods=["GET"])
async def handler():
    return web.json_response({})


@app.route(
    ["/by_id/{_id}/other/{value}"], type=RouteTypes.HTTP, methods=["GET"]
)
@parse_path
async def by_id(_id: int, value: int):
    return web.json_response({"url-param-value": f"{_id}, {value}"})


@app.route(["/one-param"], type=RouteTypes.HTTP, methods=["GET"])
async def one_param(r: RequestWrapper):
    return web.json_response(dict(r.http_request.query))


app.run()
