import functools
import json
from urllib.parse import urljoin

import cloudpickle as pickle
from exceptions import handle_error_response
from session import NeuroAPISession


def compute_this(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return DistProc(func, *args, **kwargs)

    return wrapper


class DistProc:
    def __init__(self, func, *args, host="http://localhost:3003", **kwargs) -> None:
        self.host = host
        self.session = NeuroAPISession()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def url(self, path):
        return urljoin(self.host, path)

    def run(self, debug=False):
        """Run remote procedure"""
        pickled = pickle.dumps(self.func)
        res = self._request(
            "rpc",
            {
                "args": self.args,
                "kwargs": self.kwargs,
                "name": self.func.__name__,
                "function": json.dumps(pickled.decode("latin-1")),
            },
        )
        if debug:
            return res
        return res["result"]

    def _request(self, method, params=None):
        data = {
            "method": method,
        }
        if params:
            data["params"] = params

        resp = self.session.request("POST", self.url("rpc"), json=data)
        if resp.status_code >= 400:
            handle_error_response(resp)
        resp_json = resp.json()
        return resp_json
