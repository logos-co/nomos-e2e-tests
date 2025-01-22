import pytest

from src.libs.custom_logger import get_custom_logger
from src.steps.da import StepsDataAvailability
from src.test_data import DATA_TO_DISPERSE

logger = get_custom_logger(__name__)


class TestDataIntegrity(StepsDataAvailability):
    main_nodes = []

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
        received_data = self.get_data_range(self.node2, [0] * 31 + [1], [0] * 8, [0] * 7 + [5])
        assert DATA_TO_DISPERSE[0] == bytes(received_data[0][1]).decode("utf-8")
