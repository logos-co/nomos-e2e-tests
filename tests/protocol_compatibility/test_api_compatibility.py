import pytest

from src.libs.common import to_app_id, to_index, delay
from src.libs.custom_logger import get_custom_logger
from src.steps.consensus import StepsConsensus
from src.steps.da import StepsDataAvailability
from src.steps.storage import StepsStorage
from src.test_data import DATA_TO_DISPERSE

logger = get_custom_logger(__name__)


# Extract commitments from indexed shares
def extract_commitments(index_shares):
    aggregated_column_commitments = []
    rows_commitments = []

    for index, shares in index_shares:
        for share in shares:
            a_c_c = share["aggregated_column_commitment"]
            if a_c_c not in aggregated_column_commitments:
                aggregated_column_commitments.append(a_c_c)

            r_c = share["rows_commitments"]
            for commitment in r_c:
                if commitment not in rows_commitments:
                    rows_commitments.append(commitment)

    return aggregated_column_commitments, rows_commitments


# Parse commitments received by get_shares_commitments
def parse_commitments(commitments):
    aggregated_column_commitments = []
    rows_commitments = []
    for commitment in commitments:
        aggregated_column_commitments.append(commitment["aggregated_column_commitment"])
        for rows_commitment in commitment["rows_commitments"]:
            rows_commitments.append(rows_commitment)

    return aggregated_column_commitments, rows_commitments


class TestApiCompatibility(StepsDataAvailability, StepsConsensus, StepsStorage):
    main_nodes = []

    @pytest.mark.usefixtures("setup_2_node_cluster")
    def test_da_consensus_compatibility(self):
        self.disperse_data(DATA_TO_DISPERSE[2], to_app_id(1), to_index(0))
        delay(5)
        index_shares = self.get_data_range(self.node2, to_app_id(1), to_index(0), to_index(5))
        column_commitments, rows_commitments = extract_commitments(index_shares)

        # Get consensus headers
        headers = self.get_cryptarchia_headers(self.node2)

        # Get storage blocks for received headers and extract blob ids
        blob_ids = [
            blob["id"]
            for header in headers
            for block in [self.get_storage_block(self.node2, header)]
            if block is not None and "bl_blobs" in block
            for blob in block["bl_blobs"]
        ]

        # Get commitments for blob ids
        commitments = [self.get_shares_commitments(self.node2, blob_id) for blob_id in blob_ids]

        rcv_column_commitments, rcv_rows_commitments = parse_commitments(commitments)

        # Check commitments from shares match commitments received based on consensus data
        assert all(c in rcv_column_commitments for c in column_commitments), "Not all aggregated column commitments are present"
        assert all(r in rcv_rows_commitments for r in rows_commitments), "Not all rows commitments are present"

    @pytest.mark.usefixtures("setup_4_node_cluster")
    def test_da_cross_nodes_consensus_compatibility(self):
        self.disperse_data(DATA_TO_DISPERSE[2], to_app_id(1), to_index(0))
        delay(10)
        index_shares = self.get_data_range(self.node2, to_app_id(1), to_index(0), to_index(5))
        column_commitments, rows_commitments = extract_commitments(index_shares)

        # Get consensus headers
        headers = self.get_cryptarchia_headers(self.node3)

        # Get storage blocks for received headers and extract blob ids
        blob_ids = [
            blob["id"]
            for header in headers
            for block in [self.get_storage_block(self.node3, header)]
            if block is not None and "bl_blobs" in block
            for blob in block["bl_blobs"]
        ]

        # Get commitments for blob ids
        commitments = [self.get_shares_commitments(self.node3, blob_id) for blob_id in blob_ids]

        rcv_column_commitments, rcv_rows_commitments = parse_commitments(commitments)

        # Check commitments from shares match commitments received based on consensus data
        assert all(c in rcv_column_commitments for c in column_commitments), "Not all aggregated column commitments are present"
        assert all(r in rcv_rows_commitments for r in rows_commitments), "Not all rows commitments are present"
