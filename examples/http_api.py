from aiohttp import web

from asyncworker import App
from asyncworker.http.decorators import parse_path
from asyncworker.http.types import PathParam
from asyncworker.http.wrapper import RequestWrapper

app = App()


@app.http.get(["/", "/other"])
async def handler():
    return web.json_response({})


# @app.http.get(["/by_id/{_id}/other/{value}"])
# @parse_path
# async def by_id(_id: int, value: int):
#    return web.json_response({"url-param-value": f"{_id}, {value}"})


# @app.http.get(["/one-param"])
# async def one_param(r: RequestWrapper):
#    return web.json_response(dict(r.http_request.query))


@app.http.get(["/path/{id}/accounts"])
async def _accounts(id: PathParam[int]):
    _id: int = id.unpack()
    return web.json_response({"account_id": _id})


app.run()
