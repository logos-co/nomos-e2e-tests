import pytest

from src.libs.common import delay, generate_text_data, to_app_id, to_index
from src.libs.custom_logger import get_custom_logger
from src.steps.da import StepsDataAvailability

logger = get_custom_logger(__name__)


class TestLargeVolume(StepsDataAvailability):

    @pytest.mark.usefixtures("setup_4_node_cluster")
    @pytest.mark.parametrize(
        "setup_4_node_cluster,raw_data_size",
        [
            ({"subnet_size": 4, "dispersal_factor": 1}, 50),  # => ~~0.5kB
            ({"subnet_size": 64, "dispersal_factor": 16}, 800),  # => ~~ 4kB
            ({"subnet_size": 2048, "dispersal_factor": 512}, 53 * 1024),  # => ~~254kB, spec limit: 256kB
        ],
        indirect=["setup_4_node_cluster"],
    )
    def test_large_volume_dispersal(self, raw_data_size):
        data = generate_text_data(raw_data_size)

        try:
            response = self.disperse_data(data, to_app_id(1), to_index(0), timeout_duration=0)
        except Exception as ex:
            raise Exception(f"Dispersal was not successful with error {ex}")

        assert response.status_code == 200

        delay(5)
        rcv_data = self.get_data_range(self.node2, to_app_id(1), to_index(0), to_index(5), timeout_duration=20, interval=1)
        assert rcv_data is not None

    @pytest.mark.usefixtures("setup_2_node_cluster")
    @pytest.mark.parametrize(
        "setup_2_node_cluster,raw_data_size",
        [
            ({"subnet_size": 2, "dispersal_factor": 2}, 50),
        ],
        indirect=["setup_2_node_cluster"],
    )
    def test_large_volume_dispersal_2node(self, raw_data_size):
        self.test_large_volume_dispersal(raw_data_size)
