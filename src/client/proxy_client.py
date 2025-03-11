import json
import os
import re

from src.api_clients.invalid_rest import InvalidRest
from src.api_clients.rest import REST
from src.data_storage import DS
from src.libs.common import generate_log_prefix, delay, remove_padding
from src.libs.custom_logger import get_custom_logger
from tenacity import retry, stop_after_delay, wait_fixed

from src.client.client_vars import http_proxy
from src.docker_manager import DockerManager, stop, kill
from src.env_vars import DOCKER_LOG_DIR, NOMOS_CLI

logger = get_custom_logger(__name__)


class ProxyClient:
    def __init__(self):
        command = "configurable-http-proxy"

        logger.debug(f"ProxyClient is going to be initialized with this config {http_proxy[command]}")
        self._command = command
        self._image_name = http_proxy[command]["image"]
        self._internal_ports = http_proxy[command]["ports"]
        self._volumes = http_proxy[command]["volumes"]
        self._entrypoint = http_proxy[command]["entrypoint"]

        container_name = "proxy-client-" + generate_log_prefix()
        self._log_path = os.path.join(DOCKER_LOG_DIR, f"{container_name}__{self._image_name.replace('/', '_')}.log")
        self._docker_manager = DockerManager(self._image_name)
        self._container_name = container_name
        self._container = None
        self._api = None

        cwd = os.getcwd()
        self._volumes = [cwd + "/" + volume for volume in self._volumes]

    def run(self, input_values=None, **kwargs):
        logger.debug(f"ProxyClient starting with log path {self._log_path}")

        self._port_map = {}
        self._external_ports = self._docker_manager.generate_ports(count=1)
        self._tcp_port = self._external_ports[0]
        self._api = REST(self._tcp_port)

        logger.debug(f"Internal ports {self._internal_ports}")

        for i, port in enumerate(self._internal_ports):
            self._port_map[port] = int(self._external_ports[i])

        logger.debug(f"Port map {self._port_map}")

        cmd = [self._command]

        for flag in http_proxy[self._command]["flags"]:
            for f, indexes in flag.items():
                cmd.append(f)
                for j in indexes:
                    cmd.append(input_values[j])

        logger.debug(f"ProxyCLient command to run {cmd}")

        self._container = self._docker_manager.start_container(
            self._docker_manager.image,
            port_bindings=self._port_map,
            args=None,
            log_path=self._log_path,
            volumes=self._volumes,
            entrypoint=self._entrypoint,
            remove_container=True,
            name=self._container_name,
            command=cmd,
        )

        logger.info(f"Started container {self._container_name} from image {self._image_name}.")
        DS.client_nodes.append(self)

    def set_rest_api(self):
        self._api = REST(self._tcp_port)

    def set_invalid_rest_api(self):
        self._api = InvalidRest(self._tcp_port)

    @retry(stop=stop_after_delay(5), wait=wait_fixed(0.1), reraise=True)
    def stop(self):
        self._container = stop(self._container)

    @retry(stop=stop_after_delay(5), wait=wait_fixed(0.1), reraise=True)
    def kill(self):
        self._container = kill(self._container)

    def name(self):
        return self._container_name

    def send_dispersal_request(self, data):
        return self._api.send_dispersal_request(data)

    def send_get_data_range_request(self, data):
        return self._api.send_get_range(data)
