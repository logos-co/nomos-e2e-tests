from src.libs.custom_logger import get_custom_logger
import json
from src.api_clients.base_client import BaseClient

logger = get_custom_logger(__name__)


class REST(BaseClient):
    def __init__(self, rest_port):
        self._rest_port = rest_port

    def rest_call(self, method, endpoint, payload=None, host="127.0.0.1", port=None):
        if port is None:
            port = self._rest_port
        url = f"http://{host}:{port}/{endpoint}"
        headers = {"Content-Type": "application/json", "Connection": "close"}
        return self.make_request(method, url, headers=headers, data=payload)

    def rest_call_text(self, method, endpoint, payload=None, host="127.0.0.1", port=None):
        if port is None:
            port = self._rest_port
        url = f"http://{host}:{port}/{endpoint}"
        headers = {"accept": "text/plain", "Connection": "close"}
        return self.make_request(method, url, headers=headers, data=payload)

    def info(self):
        status_response = self.rest_call("get", "cryptarchia/info")
        return status_response.json()

    def send_dispersal_request(self, data, host=None, port=None):
        return self.rest_call("post", "disperse-data", json.dumps(data))

    def send_get_range(self, query, host=None, port=None):
        response = self.rest_call("post", "da/get-range", json.dumps(query))
        return response.json()
