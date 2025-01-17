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

    def info(self):
        status_response = self.rest_call("get", "cryptarchia/info")
        return status_response.json()

    def send_dispersal_request(self, data):
        return self.rest_call("post", "disperse-data", json.dumps(data))

    def get_range(self, app_id, data_range):
        return self.rest_call("post", "da/get-range", json.dumps({"app_id": app_id, "data_range": data_range}))
