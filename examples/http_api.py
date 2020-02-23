from aiohttp import web

from asyncworker import App, RouteTypes
from asyncworker.http.decorators import parse_path

app = App()


@app.route(["/", "/other"], type=RouteTypes.HTTP, methods=["GET"])
async def handler(req: web.Request):
    return web.json_response({})


@app.route(["/by_id/{_id}"], type=RouteTypes.HTTP, methods=["GET"])
@parse_path
async def by_id(_id: int):
    return web.json_response({"url-param-value": _id})


app.run()
