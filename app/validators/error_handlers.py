from app.templates.http_status_codes import HTTP_404_NOT_FOUND
import json
from api import app

class ErrorHandlers(app):
    def __init__(self, app):
        self.app = app

    @app.errorhandler(HTTP_404_NOT_FOUND)
    def error_handlers(e):
        return json.dumps({"error": "Not found"}), HTTP_404_NOT_FOUND

# error_handler = ErrorHandlers() 