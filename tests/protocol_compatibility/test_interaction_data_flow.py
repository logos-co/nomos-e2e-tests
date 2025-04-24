import pytest

from src.libs.common import to_app_id, to_index, delay, to_blob_id
from src.libs.custom_logger import get_custom_logger
from src.steps.consensus import StepsConsensus
from src.steps.da import StepsDataAvailability
from src.steps.mempool import StepsMempool
from src.steps.storage import StepsStorage
from src.test_data import DATA_TO_DISPERSE

logger = get_custom_logger(__name__)


def extract_da_shares(index_shares):
    return [share for _, shares in index_shares for share in shares if shares]


class TestInteractionDataFlow(StepsDataAvailability, StepsMempool):
    main_nodes = []

    @pytest.mark.usefixtures("setup_2_node_cluster")
    def test_da_dispersal_integration(self):

        self.disperse_data(DATA_TO_DISPERSE[3], to_app_id(1), to_index(0))
        delay(5)
        index_shares = self.get_data_range(self.node2, to_app_id(1), to_index(0), to_index(5))
        da_shares = extract_da_shares(index_shares)

        assert len(da_shares) == 2, "Two da_shares are expected"

        modified_da_share = da_shares[0]
        modified_da_share["share_idx"] = 7

        self.add_publish_share(self.node2, modified_da_share)

        index_shares = self.get_data_range(self.node2, to_app_id(1), to_index(0), to_index(8))
        da_shares = extract_da_shares(index_shares)

        delay(5)

        assert len(da_shares) < 3, "Modified da_share should not get published"

    @pytest.mark.usefixtures("setup_2_node_cluster")
    def test_da_mempool_interaction(self):
        self.disperse_data(DATA_TO_DISPERSE[3], to_app_id(1), to_index(0))
        self.add_dispersed_blob_info(self.node2, to_blob_id(10), to_app_id(1), to_index(0))

        delay(5)

        index_shares = self.get_data_range(self.node2, to_app_id(1), to_index(0), to_index(5))
        da_shares = extract_da_shares(index_shares)

        assert len(da_shares) == 2, "Dispersal should not be affected by additional blob info added to mempool"
