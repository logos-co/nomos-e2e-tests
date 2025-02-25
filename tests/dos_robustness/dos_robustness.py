import pytest

from src.libs.common import delay, to_app_id, to_index
from src.libs.custom_logger import get_custom_logger
from src.steps.da import StepsDataAvailability
from src.test_data import DATA_TO_DISPERSE

logger = get_custom_logger(__name__)


class TestDosRobustness(StepsDataAvailability):
    main_nodes = []

    @pytest.mark.parametrize("setup_2_node_cluster", [2], indirect=True)
    def test_spam_protection_data_uploads(self, setup_2_node_cluster):
        delay(5)
        successful_dispersals = 0
        for i in range(1000):
            try:
                self.disperse_data(DATA_TO_DISPERSE[0], to_app_id(1), to_index(0), timeout_duration=0)
                successful_dispersals = i
            except Exception as ex:
                logger.debug(f"Dispersal #{i} was not successful with error {ex}")
                break

        assert successful_dispersals < 1000, "More than 1000 consecutive dispersals were successful without any constraint"
