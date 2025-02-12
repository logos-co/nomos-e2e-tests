import json
import random

import pytest

from src.cli.nomos_cli import NomosCli
from src.libs.common import delay
from src.libs.custom_logger import get_custom_logger
from src.steps.da import StepsDataAvailability
from src.test_data import DATA_TO_DISPERSE

logger = get_custom_logger(__name__)


class TestDataIntegrity(StepsDataAvailability):
    main_nodes = []

    @pytest.mark.usefixtures("setup_4_node_cluster")
    def test_da_identify_retrieve_missing_columns(self):
        delay(5)
        self.disperse_data(DATA_TO_DISPERSE[0], [0] * 31 + [1], [0] * 8)
        delay(5)
        # Select one target node at random to get blob data for 1/2 columns
        selected_node = self.main_nodes[random.randint(1, 3)]
        rcv_data = self.get_data_range(selected_node, [0] * 31 + [1], [0] * 8, [0] * 7 + [5])
        rcv_data_json = json.dumps(rcv_data)

        cli = NomosCli(command="reconstruct")
        reconstructed_data = cli.run_reconstruct(input_values=[rcv_data_json])

        assert DATA_TO_DISPERSE[0] == reconstructed_data, "Reconstructed data are not same with original data"

    @pytest.mark.usefixtures("setup_2_node_cluster")
    def test_da_sampling_determines_data_presence(self):
        delay(5)
        self.disperse_data(DATA_TO_DISPERSE[0], [0] * 31 + [1], [0] * 8)
        delay(5)
        rcv_data = self.get_data_range(self.node2, [0] * 31 + [1], [0] * 8, [0] * 7 + [5])
        rcv_data_json = json.dumps(rcv_data)

        cli = NomosCli(command="reconstruct")
        decoded_data = cli.run_reconstruct(input_values=[rcv_data_json], decode_only=True)

        assert DATA_TO_DISPERSE[0] == decoded_data, "Retrieved data are not same with original data"
