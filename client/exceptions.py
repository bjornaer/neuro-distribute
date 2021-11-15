def handle_error_response(resp):
    # Mapping of API response codes to exception classes
    codes = {
        -1: NeuroAPIError,
        500: ParseError,
        400: InvalidRequest,
    }
    error = resp.json()
    message = error.get("message")
    code = error.get("code", -1)
    data = error.get("data", {})

    raise codes[code](message=message, code=code, data=data, response=resp)


class NeuroAPIError(Exception):
    response = None
    data = {}
    code = -1
    message = "An unknown error occurred"

    def __init__(self, message=None, code=None, data={}, response=None):
        self.response = response
        if message:
            self.message = message
        if code:
            self.code = code
        if data:
            self.data = data

    def __str__(self):
        if self.code:
            return "{}: {}".format(self.code, self.message)
        return self.message


class ParseError(NeuroAPIError):
    def __str__(self):
        if self.code:
            return "{}: {}: {}".format(self.code, self.message, self.data)
        return self.message


class InvalidRequest(NeuroAPIError):
    def __str__(self):
        if self.code:
            return "{}: {}: {}".format(self.code, self.message, self.data)
        return self.message
