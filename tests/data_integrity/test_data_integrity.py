import json
import pytest

from src.client.nomos_cli import NomosCli
from src.libs.common import delay, to_app_id, to_index
from src.libs.custom_logger import get_custom_logger
from src.steps.da import StepsDataAvailability
from src.test_data import DATA_TO_DISPERSE

logger = get_custom_logger(__name__)


class TestDataIntegrity(StepsDataAvailability):
    main_nodes = []

    @pytest.mark.usefixtures("setup_4_node_cluster")
    def test_da_identify_retrieve_missing_columns(self):
        self.disperse_data(DATA_TO_DISPERSE[1], to_app_id(1), to_index(0))
        delay(5)
        test_results = []
        # Iterate through standard nodes 1-3 to get blob data for 1/2 columns
        for node in self.main_nodes[1:4]:
            rcv_data = self.get_data_range(node, to_app_id(1), to_index(0), to_index(5))
            rcv_data_json = json.dumps(rcv_data)

            reconstructed_data = NomosCli(command="reconstruct").run(input_values=[rcv_data_json])

            if DATA_TO_DISPERSE[1] == reconstructed_data:
                test_results.append(node.name())

        assert len(test_results) > 0, "Dispersed data were not received by any node"

        logger.info(f"Dispersed data received by : {test_results}")

    @pytest.mark.usefixtures("setup_4_node_cluster")
    def test_da_disperse_retrieve_one_node_stopped(self):

        # Stop nomos node 1 - dispersal and data retrieval should be still possible
        self.main_nodes[1].stop()

        self.disperse_data(DATA_TO_DISPERSE[1], to_app_id(1), to_index(0))
        delay(5)
        test_results = []
        # Iterate through standard nodes 2-3 to get blob data for 1/2 columns
        for node in self.main_nodes[2:4]:
            rcv_data = self.get_data_range(node, to_app_id(1), to_index(0), to_index(5))
            rcv_data_json = json.dumps(rcv_data)

            reconstructed_data = NomosCli(command="reconstruct").run(input_values=[rcv_data_json])

            if DATA_TO_DISPERSE[1] == reconstructed_data:
                test_results.append(node.name())

        assert len(test_results) > 0, "Dispersed data were not received by any node"

        logger.info(f"Dispersed data received by : {test_results}")

    @pytest.mark.usefixtures("setup_2_node_cluster")
    def test_da_sampling_determines_data_presence(self):
        self.disperse_data(DATA_TO_DISPERSE[1], to_app_id(1), to_index(0))
        delay(5)
        rcv_data = self.get_data_range(self.node2, to_app_id(1), to_index(0), to_index(5))
        rcv_data_json = json.dumps(rcv_data)

        decoded_data = NomosCli(command="reconstruct").run(input_values=[rcv_data_json], decode_only=True)

        assert DATA_TO_DISPERSE[1] == decoded_data, "Retrieved data are not same with original data"

    @pytest.mark.usefixtures("setup_2_node_cluster")
    def test_da_disperse_empty_data(self):
        empty_data = b""
        response = self.disperse_data(empty_data, to_app_id(1), to_index(0), utf8=False, padding=False, timeout_duration=0)

        assert response.status_code == 400, "Dispersal of empty data should be rejected as bad request"
