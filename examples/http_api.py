from aiohttp import web

from asyncworker import App, RouteTypes

app = App()


@app.route(["/", "/other"], type=RouteTypes.HTTP, methods=["GET"])
async def handler(req: web.Request):
    return web.json_response({})


app.run()
