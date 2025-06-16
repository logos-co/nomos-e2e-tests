import pytest

from src.env_vars import CONSENSUS_SLOT_TIME
from src.libs.common import to_app_id, to_index, delay
from src.steps.da import StepsDataAvailability
from src.test_data import DATA_TO_DISPERSE


class TestDispersalResilience(StepsDataAvailability):
    main_nodes = []

    @pytest.mark.usefixtures("setup_2_node_mod_da_cluster")
    def test_integrity_kzg_commitments(self):
        # Confirm validator node has rejected dispersal request from executor - there is a mismatch between
        # column data and proofs.
        self.disperse_data(DATA_TO_DISPERSE[3], to_app_id(1), to_index(0))
        delay(CONSENSUS_SLOT_TIME)
        try:
            rcv_data = self.get_data_range(self.node2, to_app_id(1), to_index(0), to_index(5))
        except AssertionError as ae:
            assert "Get data range response is empty" in str(ae), "Get data range response should be empty"
            return

        if rcv_data:
            raise AssertionError("Get data range response should be empty")
