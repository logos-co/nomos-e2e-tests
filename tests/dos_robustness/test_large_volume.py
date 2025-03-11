import random
import pytest

from src.libs.common import to_app_id, to_index
from src.libs.custom_logger import get_custom_logger
from src.steps.da import StepsDataAvailability

logger = get_custom_logger(__name__)


def generate_large_text_data(size):
    """Generate large text data with random words"""
    words = ["lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit", "sed", "do", "eiusmod", "tempor"]

    result = []
    target_size = size
    current_size = 0

    while current_size <= target_size:
        word = random.choice(words)
        result.append(word)
        current_size = len(" ".join(result).encode("utf-8"))

    data = " ".join(result)

    while len(data.encode("utf-8")) > target_size:
        data = data[:-1]

    logger.debug(f"Raw data size: {len(data.encode("utf-8"))}\n\t{data}")

    return data


class TestLargeVolume(StepsDataAvailability):

    @pytest.mark.usefixtures("setup_4_node_cluster")
    @pytest.mark.parametrize("setup_4_node_cluster", [2048], indirect=True)
    @pytest.mark.parametrize(
        "raw_data_size",
        [
            50,
            # 70,
            # 256,
            # 10 * 1024,
            # 100 * 1024,
            # 256 * 1024,
        ],
    )
    def test_large_volume_dispersal(self, raw_data_size):
        data = generate_large_text_data(raw_data_size)

        try:
            response = self.disperse_data(data, to_app_id(1), to_index(0), timeout_duration=0)
            if response.status_code != 200:
                print(response)
        except Exception as ex:
            raise Exception(f"Dispersal was not successful with error {ex}")

        assert response.status_code == 200
