from urllib.parse import quote

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

    def cryptarchia_headers(self, from_header_id, to_header_id):
        response = self.rest_call("get", f"cryptarchia/headers?from={quote(from_header_id, safe='')}" f"&to={quote(to_header_id, safe='')}")
        return response.json()

    def da_add_share(self, data):
        response = self.rest_call("post", "da/add-share", json.dumps(data))
        return response

    def da_disperse_data(self, data):
        response = self.rest_call("post", "disperse-data", json.dumps(data))
        return response

    def da_get_range(self, query):
        response = self.rest_call("post", "da/get-range", json.dumps(query))
        return response.json()

    def da_get_commitments(self, query):
        response = self.rest_call("get", "da/get-commitments", json.dumps(query))
        return response.json()

    def da_get_share(self, query):
        response = self.rest_call("get", "da/get-share", json.dumps(query))
        return response.json()

    def da_block_peer(self, data):
        response = self.rest_call("post", "da/block-peer", json.dumps(data))
        return response

    def da_unblock_peer(self, data):
        response = self.rest_call("post", "da/unblock-peer", json.dumps(data))
        return response

    def da_blacklisted_peers(self):
        response = self.rest_call("get", "da/blacklisted-peers")
        return response.json()

    def network_info(self):
        response = self.rest_call("get", "network/info")
        return response.json()

    def storage_block(self, query):
        response = self.rest_call("get", "storage/block", json.dumps(query))
        return response.json()

    def mempool_add_tx(self, data):
        response = self.rest_call("post", "mempool/add/tx", json.dumps(data))
        return response

    def mempool_add_blobinfo(self, data):
        response = self.rest_call("post", "mempool/add/blobinfo", json.dumps(data))
        return response
