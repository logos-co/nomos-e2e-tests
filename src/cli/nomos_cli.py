import os

from src.libs.common import generate_log_prefix
from src.libs.custom_logger import get_custom_logger
from tenacity import retry, stop_after_delay, wait_fixed

from src.cli.cli_vars import nomos_cli
from src.node.docker_mananger import DockerManager
from src.env_vars import DOCKER_LOG_DIR, NOMOS_CLI

logger = get_custom_logger(__name__)


class NomosCli:
    def __init__(self, command=""):
        logger.debug(f"Cli is going to be initialized with this config {nomos_cli[command]}")
        self._command = command
        self._image_name = nomos_cli[command]["image"]
        self._internal_ports = nomos_cli[command]["ports"]
        self._volumes = nomos_cli[command]["volumes"]
        self._entrypoint = nomos_cli[command]["entrypoint"]

        container_name = "nomos-cli-" + generate_log_prefix()
        self._log_path = os.path.join(DOCKER_LOG_DIR, f"{container_name}__{self._image_name.replace('/', '_')}.log")
        self._docker_manager = DockerManager(self._image_name)
        self._container_name = container_name
        self._container = None

        cwd = os.getcwd()
        self._volumes = [cwd + "/" + volume for volume in self._volumes]

    def run(self, input_values=None, **kwargs):
        logger.debug(f"NomosCli initialized with log path {self._log_path}")

        self._port_map = {}

        cmd = [NOMOS_CLI, self._command]
        for flag in nomos_cli[self._command]["flags"]:
            for f, indexes in flag.items():
                cmd.append(f)
                for j in indexes:
                    cmd.append(input_values[j])

        logger.debug(f"NomosCli command to run {cmd}")

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
