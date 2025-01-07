from src.libs.custom_logger import get_custom_logger
import json
from urllib.parse import quote
from src.node.api_clients.base_client import BaseClient

logger = get_custom_logger(__name__)


class REST(BaseClient):
    def __init__(self, rest_port):
        self._rest_port = rest_port

    def rest_call(self, method, endpoint, payload=None):
        url = f"http://127.0.0.1:{self._rest_port}/{endpoint}"
        headers = {"Content-Type": "application/json"}
        return self.make_request(method, url, headers=headers, data=payload)

    def rest_call_text(self, method, endpoint, payload=None):
        url = f"http://127.0.0.1:{self._rest_port}/{endpoint}"
        headers = {"accept": "text/plain"}
        return self.make_request(method, url, headers=headers, data=payload)

    def status(self):
        status_response = self.rest_call("get", "cl/status")
        logger.debug(f"Status response  {status_response}")
        return status_response.json()
