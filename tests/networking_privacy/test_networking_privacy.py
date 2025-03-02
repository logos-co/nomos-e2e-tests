import pytest
import psutil

from src.libs.common import delay, to_app_id, to_index, generate_random_bytes
from src.libs.custom_logger import get_custom_logger
from src.steps.da import StepsDataAvailability
from src.test_data import DATA_TO_DISPERSE

logger = get_custom_logger(__name__)


class TestNetworkingPrivacy(StepsDataAvailability):
    main_nodes = []

    @pytest.mark.usefixtures("setup_2_node_cluster")
    def test_consumed_bandwidth_dispersal(self, setup_2_node_cluster):
        net_io = psutil.net_io_counters()
        prev_total = net_io.bytes_sent + net_io.bytes_recv

        successful_dispersals = 0
        for i in range(20):
            try:
                self.disperse_data(DATA_TO_DISPERSE[7], to_app_id(1), to_index(0))
                successful_dispersals += 1
            except Exception as ex:
                logger.warning(f"Dispersal #{i+1} was not successful with error {ex}")

            if successful_dispersals == 10:
                break

            delay(0.1)

        net_io = psutil.net_io_counters()
        curr_total = net_io.bytes_sent + net_io.bytes_recv

        consumed = curr_total - prev_total

        assert successful_dispersals == 10, "Unable to finish 10 successful dispersals"

        data_sent = 2 * successful_dispersals * len(DATA_TO_DISPERSE[7])
        overhead = (consumed - data_sent) / data_sent

        assert overhead < 400, "Dispersal overhead is too high"

    @pytest.mark.usefixtures("setup_2_node_cluster")
    def test_consumed_bandwidth_random_data_dispersal(self):
        net_io = psutil.net_io_counters()
        prev_total = net_io.bytes_sent + net_io.bytes_recv

        data_to_disperse = generate_random_bytes()
        logger.debug(f"Using random data to disperse: {list(data_to_disperse)}")

        successful_dispersals = 0
        for i in range(20):
            try:
                self.disperse_data(data_to_disperse, to_app_id(1), to_index(0), utf8=False, padding=False)
                successful_dispersals += 1
            except Exception as ex:
                logger.warning(f"Dispersal #{i} was not successful with error {ex}")

            if successful_dispersals == 10:
                break

            delay(0.1)

        net_io = psutil.net_io_counters()
        curr_total = net_io.bytes_sent + net_io.bytes_recv

        consumed = curr_total - prev_total

        assert successful_dispersals == 10, "Unable to finish 10 successful dispersals"

        data_sent = 2 * successful_dispersals * len(data_to_disperse)
        overhead = (consumed - data_sent) / data_sent

        assert overhead < 400, "Dispersal overhead is too high"
