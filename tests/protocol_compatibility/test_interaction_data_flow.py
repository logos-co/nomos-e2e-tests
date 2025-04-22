import pytest

from src.libs.common import to_app_id, to_index, delay
from src.libs.custom_logger import get_custom_logger
from src.steps.consensus import StepsConsensus
from src.steps.da import StepsDataAvailability
from src.steps.storage import StepsStorage
from src.test_data import DATA_TO_DISPERSE

logger = get_custom_logger(__name__)


def extract_da_shares(index_shares):
    return [share for _, shares in index_shares for share in shares if shares]


class TestInteractionDataFlow(StepsDataAvailability, StepsConsensus, StepsStorage):
    main_nodes = []

    @pytest.mark.usefixtures("setup_2_node_cluster")
    def test_da_dispersal_integration(self):

        self.disperse_data(DATA_TO_DISPERSE[3], to_app_id(1), to_index(0))
        delay(5)
        index_shares = self.get_data_range(self.node2, to_app_id(1), to_index(0), to_index(5))
        da_shares = extract_da_shares(index_shares)

        logger.debug(f"da_shares: {da_shares}")
