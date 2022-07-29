from flask import make_response
import json

class ErrorResponse():
    def __init__(self, msg, status):
        self.msg = msg
        self.status = status

    def __handler_response__(self):
        if not self.status:
            self.status = 200
        return make_response(json.dumps({"mensagem": self.msg}), self.status)