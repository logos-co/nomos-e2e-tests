import json

import pytest

from src.cli.nomos_cli import NomosCli
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
        delay(5)
        received_data = self.get_data_range(self.node2, [0] * 31 + [1], [0] * 8, [0] * 7 + [5])
        rcv_data_json = json.dumps(received_data)
        cli = NomosCli(command="reconstruct")
        decoded_data = cli.run_reconstruct(input_values=[rcv_data_json])

        assert DATA_TO_DISPERSE[0] == decoded_data, "Retrieved data are not same with original data"
