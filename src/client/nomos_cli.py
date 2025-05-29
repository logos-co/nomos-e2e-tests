import json
import os
import re

from src.data_storage import DS
from src.libs.common import generate_log_prefix, delay, remove_padding
from src.libs.custom_logger import get_custom_logger
from tenacity import retry, stop_after_delay, wait_fixed

from src.client.client_vars import nomos_cli
from src.docker_manager import DockerManager, stop, kill
from src.env_vars import DOCKER_LOG_DIR, NOMOS_CLI

logger = get_custom_logger(__name__)


class NomosCli:
    def __init__(self, **kwargs):
        if "command" not in kwargs:
            raise ValueError("The command parameter is required")

        command = kwargs["command"]
        if command not in nomos_cli:
            raise ValueError("Unknown command provided")

        logger.debug(f"NomosCli is going to be initialized with this config {nomos_cli[command]}")
        self._command = command
        self._image_name = nomos_cli[command]["image"]
        self._internal_ports = nomos_cli[command]["ports"]
        self._volumes = nomos_cli[command]["volumes"]
        self._entrypoint = nomos_cli[command]["entrypoint"]

        container_name = "nomos-cli_" + generate_log_prefix()
        self._log_path = os.path.join(DOCKER_LOG_DIR, f"{container_name}__{self._image_name.replace('/', '_')}.log")
        self._docker_manager = DockerManager(self._image_name)
        self._container_name = container_name
        self._container = None
        self._stop_event = None

        cwd = os.getcwd()
        self._volumes = [cwd + "/" + volume for volume in self._volumes]

    def run(self, input_values=None, **kwargs):
        logger.debug(f"NomosCli starting with log path {self._log_path}")

        self._port_map = {}

        cmd = [NOMOS_CLI, self._command]
        for flag in nomos_cli[self._command]["flags"]:
            for f, indexes in flag.items():
                cmd.append(f)
                for j in indexes:
                    cmd.append(input_values[j])

        logger.debug(f"NomosCli command to run {cmd}")

        self._container, self._stop_event = self._docker_manager.start_container(
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

        match self._command:
            case "reconstruct":
                decode_only = kwargs.get("decode_only", False)
                return self.reconstruct(decode_only=decode_only)
            case _:
                return

    def reconstruct(self, decode_only=False):
        keyword = "Reconstructed data"
        keywords = [keyword]

        log_stream = self._container.logs(stream=True)

        matches = self._docker_manager.search_log_for_keywords(self._log_path, keywords, False, log_stream)
        assert len(matches[keyword]) > 0, f"Reconstructed data not found {matches[keyword]}"

        logger.debug(f"Reconstructed data match found {matches[keyword]}")

        # Use regular expression that captures the byte list after "Reconstructed data"
        result = re.sub(r".*Reconstructed data\s*(\[[^\]]+\]).*", r"\1", matches[keyword][0])

        result_bytes = []
        try:
            result_bytes = json.loads(result)
        except Exception as ex:
            logger.debug(f"Conversion to bytes failed with exception {ex}")

        if decode_only:
            result_bytes = result_bytes[:-31]

        result_bytes = remove_padding(result_bytes)
        result = bytes(result_bytes).decode("utf-8")

        DS.client_nodes.remove(self)

        return result

    @retry(stop=stop_after_delay(5), wait=wait_fixed(0.1), reraise=True)
    def stop(self):
        self._container = stop(self._container, self._stop_event)

    @retry(stop=stop_after_delay(5), wait=wait_fixed(0.1), reraise=True)
    def kill(self):
        self._container = kill(self._container, self._stop_event)

    def name(self):
        return self._container_name
