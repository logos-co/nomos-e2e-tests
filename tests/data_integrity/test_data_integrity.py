import json
import subprocess

import pytest

from src.env_vars import NOMOS_CLI
from src.libs.common import delay
from src.libs.custom_logger import get_custom_logger
from src.steps.da import StepsDataAvailability
from src.test_data import DATA_TO_DISPERSE

logger = get_custom_logger(__name__)


class TestDataIntegrity(StepsDataAvailability):
    main_nodes = []

    @pytest.mark.skip(reason="Waiting for PR https://github.com/logos-co/nomos-node/pull/994")
    @pytest.mark.usefixtures("setup_5_node_cluster")
    def test_da_identify_retrieve_missing_columns(self):
        self.disperse_data(DATA_TO_DISPERSE[0], [0] * 31 + [1], [0] * 8)
        received_data = []
        # Get data only from half of nodes
        for node in self.main_nodes[2:4]:
            received_data.append(self.get_data_range(node, [0] * 31 + [1], [0] * 8, [0] * 7 + [3]))

        # Use received blob data to reconstruct the original data
        # nomos-cli reconstruct command required
        reconstructed_data = []
        assert DATA_TO_DISPERSE[0] == bytes(reconstructed_data).decode("utf-8")

    @pytest.mark.usefixtures("setup_2_node_cluster")
    def test_da_sampling_determines_data_presence(self):
        self.disperse_data(DATA_TO_DISPERSE[0], [0] * 31 + [1], [0] * 8)
        delay(10)
        received_data = self.get_data_range(self.node2, [0] * 31 + [1], [0] * 8, [0] * 7 + [5])
        rcv_data_json = json.dumps(received_data)
        cmd = str(NOMOS_CLI + " reconstruct --app-blobs " + "'" + str(rcv_data_json) + "'")

        logger.debug(f"Command to run {cmd}")

        cmd_type = type(cmd)
        logger.debug(f"Command type {cmd_type}")

        try:
            completed_cmd = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
            logger.debug(f"Command finished with output {completed_cmd.stdout}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error occurred while running nomos-cli {e.stderr}")

        # assert DATA_TO_DISPERSE[0] == bytes(received_data[0][1]).decode("utf-8")
