import random
import pytest

from src.libs.common import delay, to_app_id, to_index, random_divide_k, generate_random_bytes
from src.libs.custom_logger import get_custom_logger
from src.steps.da import StepsDataAvailability
from src.test_data import DATA_TO_DISPERSE

logger = get_custom_logger(__name__)


class TestDosRobustness(StepsDataAvailability):
    main_nodes = []

    @pytest.mark.usefixtures("setup_2_node_cluster")
    def test_spam_protection_valid_uploads(self):
        num_samples = len(DATA_TO_DISPERSE)
        missing_dispersals = num_samples
        for i in range(num_samples):
            try:
                response = self.disperse_data(DATA_TO_DISPERSE[i], to_app_id(1), to_index(0), timeout_duration=0)
                if response.status_code == 200:
                    missing_dispersals -= 1
            except Exception as ex:
                raise Exception(f"Dispersal #{i+1} was not successful with error {ex}")

            delay(0.1)

        assert missing_dispersals == 0, f"{missing_dispersals} dispersals were not successful"

    @pytest.mark.usefixtures("setup_2_node_cluster")
    def test_spam_protection_single_burst(self):
        rate_limit = 1000
        spam_per_burst = rate_limit + 10
        successful_dispersals = 0
        for i in range(spam_per_burst):
            try:
                response = self.disperse_data(DATA_TO_DISPERSE[0], to_app_id(1), to_index(0), timeout_duration=0)
                if response.status_code == 429:
                    break
                else:
                    successful_dispersals += 1
            except Exception as ex:
                raise Exception(f"Dispersal #{i+1} was not successful with error {ex}")

        assert successful_dispersals <= rate_limit, "All consecutive dispersals were successful without any constraint"

    @pytest.mark.usefixtures("setup_2_node_cluster")
    def test_spam_protection_random_bytes_single_burst(self):
        rate_limit = 1000
        spam_per_burst = rate_limit + 10

        n = random.randint(1, 256)
        data_to_disperse = generate_random_bytes(n)

        successful_dispersals = 0
        for i in range(spam_per_burst):
            try:
                response = self.disperse_data(data_to_disperse, to_app_id(1), to_index(0), timeout_duration=0, utf8=False)
                if response.status_code == 429:
                    break
                else:
                    successful_dispersals += 1
            except Exception as ex:
                raise Exception(f"Dispersal #{i+1} was not successful with error {ex}")

        assert successful_dispersals <= rate_limit, "All consecutive dispersals were successful without any constraint"

    @pytest.mark.usefixtures("setup_2_node_cluster")
    def test_spam_protection_multiple_bursts(self):
        time_interval = 60
        rate_limit = 1000
        bursts = 3
        spam_per_burst = int((rate_limit + 10) / bursts)

        waiting_intervals = random_divide_k(time_interval, bursts)

        logger.debug(f"Waiting intervals: {waiting_intervals}")

        successful_dispersals = 0
        for b in range(bursts):
            for i in range(spam_per_burst):
                try:
                    response = self.disperse_data(DATA_TO_DISPERSE[7], to_app_id(1), to_index(0), timeout_duration=0)
                    if response.status_code == 429:
                        break
                    else:
                        successful_dispersals += 1
                except Exception as ex:
                    raise Exception(f"Dispersal #{i+1} was not successful with error {ex}")

            delay(waiting_intervals[b])

        assert successful_dispersals <= 1000, "All dispersals were successful without any constraint"
