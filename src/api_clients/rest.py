from src.libs.custom_logger import get_custom_logger
import json
from src.api_clients.base_client import BaseClient

logger = get_custom_logger(__name__)


class REST(BaseClient):
    def __init__(self, rest_port):
        self._rest_port = rest_port

    def rest_call(self, method, endpoint, payload=None):
        url = f"http://localhost:{self._rest_port}/{endpoint}"
        headers = {"Content-Type": "application/json", "Connection": "close"}
        return self.make_request(method, url, headers=headers, data=payload)

    def rest_call_text(self, method, endpoint, payload=None):
        url = f"http://localhost:{self._rest_port}/{endpoint}"
        headers = {"accept": "text/plain", "Connection": "close"}
        return self.make_request(method, url, headers=headers, data=payload)

    def cl_metrics(self):
        response = self.rest_call("get", "cl/metrics")
        return response.json()

    def cl_status(self, query):
        response = self.rest_call("post", "cl/status", json.dumps(query))
        return response.json()

    def cryptarchia_info(self):
        response = self.rest_call("get", "cryptarchia/info")
        return response.json()

    def da_disperse_data(self, data):
        response = self.rest_call("post", "disperse-data", json.dumps(data))
        return response

    def da_get_range(self, query):
        response = self.rest_call("post", "da/get-range", json.dumps(query))
        return response.json()
