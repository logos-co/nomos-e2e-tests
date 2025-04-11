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
        shares = self.get_data_range(self.node2, to_app_id(1), to_index(0), to_index(5))
        logger.debug(f"shares: {shares}")
        aggregated_column_commitments = []
        rows_commitments = []
        for index_share in shares:
            if len(index_share[1]) != 0:
                for share in index_share[1]:
                    a_c_c = share["aggregated_column_commitment"]
                    if a_c_c not in aggregated_column_commitments:
                        aggregated_column_commitments.append(a_c_c)

                    r_c = share["rows_commitments"]
                    for commitment in r_c:
                        if commitment not in rows_commitments:
                            rows_commitments.append(commitment)

        headers = self.get_cryptarchia_headers(self.node2)

        # Get storage blocks for headerIDs
        blob_ids = []
        for header in headers:
            block = self.get_storage_block(self.node2, header)
            if block is not None and "bl_blobs" in block:
                blobs = block["bl_blobs"]
                for blob in blobs:
                    blob_ids.append(blob["id"])

        # Get commitments for blob ids
        commitments = []
        for blob_id in blob_ids:
            commitment = self.get_shares_commitments(self.node2, blob_id)
            commitments.append(commitment)

        rcv_aggregated_column_commitments = []
        rcv_rows_commitments = []
        for commitment in commitments:
            rcv_aggregated_column_commitments.append(commitment["aggregated_column_commitment"])
            for rcv_rows_commitment in commitment["rows_commitments"]:
                rcv_rows_commitments.append(rcv_rows_commitment)

        # Check commitments from shares match commitments received based on consensus data
        for a_c_c in aggregated_column_commitments:
            assert a_c_c in rcv_aggregated_column_commitments

        for r_c in rows_commitments:
            assert r_c in rcv_rows_commitments
