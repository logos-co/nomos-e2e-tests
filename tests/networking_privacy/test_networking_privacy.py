import pytest

from src.libs.common import delay, to_app_id, to_index
from src.steps.da import StepsDataAvailability
from src.test_data import DATA_TO_DISPERSE


class TestNetworkingPrivacy(StepsDataAvailability):
    main_nodes = []

    @pytest.mark.parametrize("setup_2_node_cluster", [1024], indirect=True)
    def test_consumed_bandwidth_dispersal(self, setup_2_node_cluster):
        delay(5)
        self.disperse_data(DATA_TO_DISPERSE[1], to_app_id(1), to_index(0))
