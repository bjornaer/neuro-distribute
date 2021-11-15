from tornado.web import Application, url

from .handler import MainHandler, RPCHandler


def make_app(executor):
    return Application(
        [
            url(r"/rpc", RPCHandler, {"executor": executor}),
            url(r"/", MainHandler),
        ]
    )
