import json
import os

from src.libs.custom_logger import get_custom_logger
from tenacity import retry, stop_after_delay, wait_fixed

from src.node.api_clients.rest import REST
from src.node.docker_mananger import DockerManager
from src.env_vars import DOCKER_LOG_DIR
from src.node.node_vars import nomos_nodes

logger = get_custom_logger(__name__)


def sanitize_docker_flags(input_flags):
    output_flags = {}
    for key, value in input_flags.items():
        key = key.replace("_", "-")
        output_flags[key] = value

    return output_flags


class NomosNode:
    def __init__(self, node_type, docker_log_prefix=""):
        print(nomos_nodes)
        self._image_name = nomos_nodes[node_type]["image"]
        self._internal_ports = nomos_nodes[node_type]["ports"]
        self._volumes = nomos_nodes[node_type]["volumes"]
        self._entrypoint = nomos_nodes[node_type]["entrypoint"]

        self._log_path = os.path.join(DOCKER_LOG_DIR, f"{docker_log_prefix}__{self._image_name.replace('/', '_')}.log")
        self._docker_manager = DockerManager(self._image_name)
        self._container = None
        logger.debug(f"NomosNode instance initialized with log path {self._log_path}")

    @retry(stop=stop_after_delay(60), wait=wait_fixed(0.1), reraise=True)
    def start(self, wait_for_node_sec=20, **kwargs):
        logger.debug("Starting Node...")
        self._docker_manager.create_network()
        self._ext_ip = self._docker_manager.generate_random_ext_ip()
        self._ports = self._docker_manager.generate_ports(count=len(self._internal_ports))
        self._udp_port = self._ports[0]
        self._tcp_port = self._ports[1]
        self._api = REST(self._tcp_port)

        default_args = {
            "listen-address": "0.0.0.0",
            "log-level": "info",
            "nat": f"extip:{self._ext_ip}",
        }

        logger.debug(f"Using volumes {self._volumes}")

        self._container = self._docker_manager.start_container(
            self._docker_manager.image,
            ports=self._ports,
            args=default_args,
            log_path=self._log_path,
            container_ip=self._ext_ip,
            volumes=self._volumes,
            remove_container=True,
        )

        logger.debug(f"Started container from image {self._image_name}")
