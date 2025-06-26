import io
import os
import tarfile

from src.data_storage import DS
from src.libs.common import generate_log_prefix
from src.libs.custom_logger import get_custom_logger
from tenacity import retry, stop_after_delay, wait_fixed

from src.api_clients.rest import REST
from src.docker_manager import DockerManager, stop, kill
from src.env_vars import DOCKER_LOG_DIR
from src.node.node_vars import nomos_nodes
from src.test_data import LOG_ERROR_KEYWORDS
from src.tfidf.tfidf import LogTfidf

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

        log_prefix = generate_log_prefix()
        self._log_path = os.path.join(DOCKER_LOG_DIR, f"{container_name}_{log_prefix}__{self._image_name.replace('/', '_')}.log")
        self._docker_manager = DockerManager(self._image_name)
        self._container_name = container_name
        self._container = None
        self._stop_event = None

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

        self._container, self._stop_event = self._docker_manager.start_container(
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
        self._container = stop(self._container, self._stop_event)

    @retry(stop=stop_after_delay(5), wait=wait_fixed(0.1), reraise=True)
    def kill(self):
        self._container = kill(self._container, self._stop_event)

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
            try:
                check_ready()
            except Exception as ex:
                logger.error(f"REST service did not become ready in time: {ex}")
                raise

    def is_nomos(self):
        return "nomos" in self._container_name

    def info(self):
        return self._api.cryptarchia_info()

    def node_type(self):
        return self._node_type

    def name(self):
        return self._container_name

    def get_archive(self, path):
        return self._container.get_archive(path)

    def api_port(self):
        return self._tcp_port

    def api_port_internal(self):
        for internal_port, external_port in self._port_map.items():
            if str(external_port).replace("/tcp", "") == self._tcp_port:
                return internal_port.replace("/tcp", "")
        return None

    def check_nomos_log_errors(self):
        keywords = LOG_ERROR_KEYWORDS

        logger.debug(f"Parsing log for node {self.name()}")
        log_tfidf = LogTfidf()
        log_tfidf.parse_log(self._log_path, f"{self._log_path}.parsed", keywords, True)

    def extract_config(self, target_file):
        # Copy the config file from first node
        stream, _stat = self.get_archive("/config.yaml")

        # Join stream into bytes and load into a memory buffer
        tar_bytes = io.BytesIO(b"".join(stream))

        # Extract and write only the actual config file
        with tarfile.open(fileobj=tar_bytes) as tar:
            member = tar.getmembers()[0]
            file_obj = tar.extractfile(member)
            if file_obj:
                with open(f"{target_file}", "wb") as f:
                    f.write(file_obj.read())

    def send_dispersal_request(self, data):
        return self._api.da_disperse_data(data)

    def send_get_data_range_request(self, data):
        return self._api.da_get_range(data)

    def send_get_commitments_request(self, data):
        return self._api.da_get_commitments(data)

    def send_get_storage_block_request(self, data):
        return self._api.storage_block(data)

    def send_get_cryptarchia_headers_request(self, data):
        return self._api.cryptarchia_headers(data)

    def send_add_share_request(self, data):
        return self._api.da_add_share(data)

    def send_add_blob_info_request(self, data):
        return self._api.mempool_add_blobinfo(data)
