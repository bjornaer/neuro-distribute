import requests


class NeuroAPISession(requests.Session):
    def __init__(self, *args, **kwargs):
        super(NeuroAPISession, self).__init__(*args, **kwargs)

        self.headers.update(
            {"Accept-Charset": "utf-8", "Content-Type": "application/json"}
        )
