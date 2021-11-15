import json
import logging

import cloudpickle as pickle
import tornado.ioloop
import tornado.web

logger = logging.getLogger(__name__)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Welcome to the Neuro API challenge")


class RPCHandler(tornado.web.RequestHandler):
    def initialize(self, executor):
        # this is brought here to enable looking into it
        self.executor = executor

    def get(self):
        self.write("I work on a POST basis")

    async def post(self):
        data = tornado.escape.json_decode(self.request.body)
        logger.debug(data)
        try:
            # get function details
            name = data["params"]["name"]
            args = data["params"]["args"]
            kwargs = data["params"]["kwargs"]
            logger.debug("Executing rpc request function %s", name)
            string_f = data["params"]["function"]

            # parse function code back to python object
            bytes_f = json.loads(string_f).encode("latin-1")
            func = pickle.loads(bytes_f)

            # run function in loop thread executor
            loop = tornado.ioloop.IOLoop.current()
            res = await loop.run_in_executor(None, func, *args, **kwargs)

            # look into executor for details regarding workers and queue
            q_size = self.executor._work_queue.qsize()
            threads = len(self.executor._threads)
            logger.debug("RESULT: %d QUEUE: %d THREADS: %d", res, q_size, threads)

            # return results to client
            self.write({"result": res, "queued_tasks": q_size, "workers": threads})
        except KeyError as err:
            logger.error("missing key [%s] in request", err.args[0])
            self.set_status(400)
            self.finish(
                {
                    "message": "Invalid request",
                    "code": 400,
                    "data": f"missing parameter {err.args[0]}",
                }
            )
        except (NameError, ModuleNotFoundError) as err:
            logger.error("parsing error on remote call")
            self.set_status(500)
            self.finish({"message": "Parsing error", "data": err.args[0], "code": 500})
