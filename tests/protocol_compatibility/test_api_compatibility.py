import json
import pytest

from src.client.nomos_cli import NomosCli
from src.libs.common import to_app_id, to_index, delay
from src.libs.custom_logger import get_custom_logger
from src.steps.consensus import StepsConsensus
from src.steps.da import StepsDataAvailability
from src.steps.storage import StepsStorage
from src.test_data import DATA_TO_DISPERSE

logger = get_custom_logger(__name__)


class TestApiCompatibility(StepsDataAvailability, StepsConsensus, StepsStorage):
    main_nodes = []

    @pytest.mark.usefixtures("setup_2_node_cluster")
    def test_da_consensus_compatibility(self):
        self.disperse_data(DATA_TO_DISPERSE[2], to_app_id(1), to_index(0))
        delay(5)
        rcv_data = self.get_data_range(self.node2, to_app_id(1), to_index(0), to_index(5))
        logger.debug(f"shares: {rcv_data}")
        headers = self.get_cryptarchia_headers(self.node2)
        logger.debug(f"headers: {headers}")
        # get storage blocks for headerID
        blob_ids = []
        for header in headers:
            block = self.get_storage_block(self.node2, header)
            if block is not None and "bl_blobs" in block:
                blobs = block["bl_blobs"]
                for blob in blobs:
                    blob_ids.append(blob["id"])

        logger.debug(f"blob ids: {blob_ids}")
