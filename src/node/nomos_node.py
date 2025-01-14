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
    def __init__(self, node_type, container_name=""):
        logger.debug(f"Node is going to be initialized with this config {nomos_nodes[node_type]}")
        self._image_name = nomos_nodes[node_type]["image"]
        self._internal_ports = nomos_nodes[node_type]["ports"]
        self._volumes = nomos_nodes[node_type]["volumes"]
        self._entrypoint = nomos_nodes[node_type]["entrypoint"]

        self._log_path = os.path.join(DOCKER_LOG_DIR, f"{container_name}__{self._image_name.replace('/', '_')}.log")
        self._docker_manager = DockerManager(self._image_name)
        self._container_name = container_name
        self._container = None

        cwd = os.getcwd()
        for i, volume in enumerate(self._volumes):
            self._volumes[i] = cwd + "/" + volume

        logger.debug(f"NomosNode instance initialized with log path {self._log_path}")

    @retry(stop=stop_after_delay(60), wait=wait_fixed(0.1), reraise=True)
    def start(self, wait_for_node_sec=120, **kwargs):
        logger.debug("Starting Node...")
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

        logger.debug(f"Container returned  {self._container}")
        logger.debug(f"Started container from image {self._image_name}. " f"REST: {getattr(self, '_tcp_port', 'N/A')}")

    @retry(stop=stop_after_delay(5), wait=wait_fixed(0.1), reraise=True)
    def stop(self):
        if self._container:
            logger.debug(f"Stopping container with id {self._container.short_id}")
            self._container.stop()
            try:
                self._container.remove()
            except:
                pass
            self._container = None
            logger.debug("Container stopped.")

    @retry(stop=stop_after_delay(5), wait=wait_fixed(0.1), reraise=True)
    def kill(self):
        if self._container:
            logger.debug(f"Killing container with id {self._container.short_id}")
            self._container.kill()
            try:
                self._container.remove()
            except:
                pass
            self._container = None
            logger.debug("Container killed.")

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
