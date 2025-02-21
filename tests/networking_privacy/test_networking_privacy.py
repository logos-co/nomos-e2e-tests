import pytest
import psutil

from src.libs.common import delay, to_app_id, to_index
from src.libs.custom_logger import get_custom_logger
from src.steps.da import StepsDataAvailability
from src.test_data import DATA_TO_DISPERSE

logger = get_custom_logger(__name__)


class TestNetworkingPrivacy(StepsDataAvailability):
    main_nodes = []

    @pytest.mark.parametrize("setup_2_node_cluster", [1024], indirect=True)
    def test_consumed_bandwidth_dispersal(self, setup_2_node_cluster):
        delay(5)
        net_io = psutil.net_io_counters()
        prev_total = net_io.bytes_sent + net_io.bytes_recv
        self.disperse_data(DATA_TO_DISPERSE[1], to_app_id(1), to_index(0))
        net_io = psutil.net_io_counters()
        curr_total = net_io.bytes_sent + net_io.bytes_recv

        logger.debug(f"prev_total: {prev_total}")
        logger.debug(f"curr_total: {curr_total}")

        consumed = curr_total - prev_total

        logger.debug(f"consumed: {consumed}")

        delay(5)
        rcv_data = self.get_data_range(self.node2, to_app_id(1), to_index(0), to_index(5))
        logger.debug(f"Received data: {rcv_data}")
