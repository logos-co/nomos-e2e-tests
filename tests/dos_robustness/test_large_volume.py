import pytest

from src.libs.common import generate_text_data, to_app_id, to_index
from src.libs.custom_logger import get_custom_logger
from src.steps.da import StepsDataAvailability

logger = get_custom_logger(__name__)


class TestLargeVolume(StepsDataAvailability):

    @pytest.mark.usefixtures("setup_4_node_cluster")
    @pytest.mark.parametrize(
        "setup_4_node_cluster,raw_data_size",
        [
            ({"subnet_size": 32, "dispersal_factor": 8}, 70),  # => ~~0.58kB
            ({"subnet_size": 2048, "dispersal_factor": 512}, 51 * 1024),  # => ~~244kB, spec limit: 248kB
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
