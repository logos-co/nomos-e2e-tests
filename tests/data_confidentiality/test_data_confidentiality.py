import json

import pytest

from src.client.nomos_cli import NomosCli
from src.env_vars import CONSENSUS_SLOT_TIME, NOMOS
from src.libs.common import delay, to_app_id, to_index
from src.libs.custom_logger import get_custom_logger
from src.node.nomos_node import NomosNode
from src.steps.common import ensure_nodes_ready
from src.steps.da import StepsDataAvailability
from src.test_data import DATA_TO_DISPERSE

logger = get_custom_logger(__name__)


class TestDataConfidentiality(StepsDataAvailability):
    main_nodes = []

    @pytest.mark.usefixtures("setup_2_node_cluster")
    def test_unauthorized_node_cannot_receive_dispersed_data(self):
        self.disperse_data(DATA_TO_DISPERSE[1], to_app_id(1), to_index(0))
        delay(CONSENSUS_SLOT_TIME)
        rcv_data = self.get_data_range(self.node2, to_app_id(1), to_index(0), to_index(5))
        rcv_data_json = json.dumps(rcv_data)

        decoded_data = NomosCli(command="reconstruct").run(input_values=[rcv_data_json], decode_only=True)

        assert DATA_TO_DISPERSE[1] == decoded_data, "Retrieved data are not same with original data"
        self.node2.stop()
        # Start new node with the same IP address
        self.nodeX = NomosNode(NOMOS, "nomos_node_0")
        self.nodeX.start()

        try:
            ensure_nodes_ready(self.nodeX)
        except Exception as ex:
            logger.error(f"REST service did not become ready in time: {ex}")
            raise

        delay(CONSENSUS_SLOT_TIME)

        self.disperse_data(DATA_TO_DISPERSE[2], to_app_id(2), to_index(0))
        delay(CONSENSUS_SLOT_TIME)
        try:
            rcv_data = self.get_data_range(self.nodeX, to_app_id(2), to_index(0), to_index(5))
        except AssertionError as ae:
            assert "Get data range response is empty" in str(ae), "Get data range response should be empty"
