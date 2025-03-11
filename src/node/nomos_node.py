import os

from src.data_storage import DS
from src.libs.custom_logger import get_custom_logger
from tenacity import retry, stop_after_delay, wait_fixed

from src.api_clients.rest import REST
from src.docker_manager import DockerManager, stop, kill
from src.env_vars import DOCKER_LOG_DIR
from src.node.node_vars import nomos_nodes
from src.test_data import LOG_ERROR_KEYWORDS

logger = get_custom_logger(__name__)


def sanitize_docker_flags(input_flags):
    output_flags = {}
    for key, value in input_flags.items():
        key = key.replace("_", "-")
        output_flags[key] = value

    return output_flags


class NomosNode:
    def __init__(self, node_type, container_name=""):
        logger.debug(f"Node is going to be initialized with this config {nomos_nodes[node_type]}")
        self._image_name = nomos_nodes[node_type]["image"]
        self._internal_ports = nomos_nodes[node_type]["ports"]
        self._volumes = nomos_nodes[node_type]["volumes"]
        self._entrypoint = nomos_nodes[node_type]["entrypoint"]
        self._node_type = node_type

        self._log_path = os.path.join(DOCKER_LOG_DIR, f"{container_name}__{self._image_name.replace('/', '_')}.log")
        self._docker_manager = DockerManager(self._image_name)
        self._container_name = container_name
        self._container = None

        cwd = os.getcwd()
        self._volumes = [cwd + "/" + volume for volume in self._volumes]

        logger.debug(f"NomosNode instance initialized with log path {self._log_path}")

    @retry(stop=stop_after_delay(60), wait=wait_fixed(0.1), reraise=True)
    def start(self, wait_for_node_sec=120, **kwargs):
        logger.debug(f"Starting Node {self._container_name} with role {self._node_type}")
        self._docker_manager.create_network()
        self._ext_ip = self._docker_manager.generate_random_ext_ip()

        number_of_ports = len(self._internal_ports)
        self._port_map = {}

        if number_of_ports > 0:
            self._external_ports = self._docker_manager.generate_ports(count=number_of_ports)
            self._udp_port = self._external_ports[0]
            self._tcp_port = self._external_ports[1]
            self._api = REST(self._tcp_port)

        logger.debug(f"Internal ports {self._internal_ports}")

        for i, port in enumerate(self._internal_ports):
            self._port_map[port] = int(self._external_ports[i])

        default_args = {}

        logger.debug(f"Using volumes {self._volumes}")

        logger.debug(f"Port map {self._port_map}")

        self._container = self._docker_manager.start_container(
            self._docker_manager.image,
            port_bindings=self._port_map,
            args=default_args,
            log_path=self._log_path,
            volumes=self._volumes,
            entrypoint=self._entrypoint,
            remove_container=True,
            name=self._container_name,
        )

        logger.info(f"Started container {self._container_name} from image {self._image_name}. " f"REST: {getattr(self, '_tcp_port', 'N/A')}")
        DS.nomos_nodes.append(self)

    @retry(stop=stop_after_delay(5), wait=wait_fixed(0.1), reraise=True)
    def stop(self):
        self._container = stop(self._container)

    @retry(stop=stop_after_delay(5), wait=wait_fixed(0.1), reraise=True)
    def kill(self):
        self._container = kill(self._container)

    def restart(self):
        if self._container:
            logger.debug(f"Restarting container with id {self._container.short_id}")
            self._container.restart()

    def pause(self):
        if self._container:
            logger.debug(f"Pausing container with id {self._container.short_id}")
            self._container.pause()

    def unpause(self):
        if self._container:
            logger.debug(f"Unpause container with id {self._container.short_id}")
            self._container.unpause()

    def ensure_ready(self, timeout_duration=10):
        @retry(stop=stop_after_delay(timeout_duration), wait=wait_fixed(0.1), reraise=True)
        def check_ready(node=self):
            node.info_response = node.info()
            logger.info("REST service is ready !!")

        if self.is_nomos():
            check_ready()

    def is_nomos(self):
        return "nomos" in self._container_name

    def info(self):
        return self._api.info()

    def node_type(self):
        return self._node_type

    def name(self):
        return self._container_name

    def api_port(self):
        return self._tcp_port

    def api_port_internal(self):
        for internal_port, external_port in self._port_map.items():
            if str(external_port).replace("/tcp", "") == self._tcp_port:
                return internal_port.replace("/tcp", "")
        return None

    def check_nomos_log_errors(self, whitelist=None):
        keywords = LOG_ERROR_KEYWORDS

        # If a whitelist is provided, remove those keywords from the keywords list
        if whitelist:
            keywords = [keyword for keyword in keywords if keyword not in whitelist]

        matches_found = self._docker_manager.search_log_for_keywords(self._log_path, keywords, False)

        logger.info(f"Printing log matches for {self.name()}")
        if matches_found:
            for keyword, log_lines in matches_found.items():
                for line in log_lines:
                    logger.debug(f"Log line matching keyword '{keyword}': {line}")
        else:
            logger.debug("No keyword matches found in the logs.")

    def send_dispersal_request(self, data):
        return self._api.send_dispersal_request(data)

    def send_get_data_range_request(self, data):
        return self._api.send_get_range(data)
