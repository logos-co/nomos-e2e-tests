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

    @pytest.mark.usefixtures("setup_2_node_cluster")
    def test_da_sampling_determines_data_presence(self):
        self.disperse_data(DATA_TO_DISPERSE[0], [0] * 31 + [1], [0] * 8)
        received_data = self.get_data_range([0] * 31 + [1], [0] * 8, [0] * 7 + [5])
        assert DATA_TO_DISPERSE[0] == bytes(received_data[0][1]).decode("utf-8")
