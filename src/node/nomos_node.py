import os

from src.libs.custom_logger import get_custom_logger
from tenacity import retry, stop_after_delay, wait_fixed
from src.node.api_clients.rest import REST
from src.node.docker_mananger import DockerManager
from src.env_vars import DOCKER_LOG_DIR

logger = get_custom_logger(__name__)


def sanitize_docker_flags(input_flags):
    output_flags = {}
    for key, value in input_flags.items():
        key = key.replace("_", "-")
        output_flags[key] = value

    return output_flags


class NomosNode:
    def __init__(self, docker_image, docker_log_prefix=""):
        self._image_name = docker_image
        self._log_path = os.path.join(DOCKER_LOG_DIR, f"{docker_log_prefix}__{self._image_name.replace('/', '_')}.log")
        self._docker_manager = DockerManager(self._image_name)
        self._container = None
        logger.debug(f"NomosNode instance initialized with log path {self._log_path}")

    @retry(stop=stop_after_delay(60), wait=wait_fixed(0.1), reraise=True)
    def start(self, wait_for_node_sec=20, **kwargs):
        logger.debug("Starting Node...")
