import allure

from src.env_vars import NOMOS_EXECUTOR
from src.steps.common import StepsCommon


def add_padding(orig_bytes):
    block_size = 31
    """
    Pads a list of bytes (integers in [0..255]) using a PKCS#7-like scheme:
    - The value of each padded byte is the number of bytes padded.
    - If the original data is already a multiple of the block size,
      an additional full block of bytes (each the block size) is added.
    """
    original_len = len(orig_bytes)
    padding_needed = block_size - (original_len % block_size)
    # If the data is already a multiple of block_size, add a full block of padding
    if padding_needed == 0:
        padding_needed = block_size

    # Each padded byte will be equal to padding_needed
    padded_bytes = orig_bytes + [padding_needed] * padding_needed
    return padded_bytes


def prepare_dispersal_request(data, app_id, index):
    data_bytes = data.encode("utf-8")
    padded_bytes = add_padding(list(data_bytes))
    dispersal_data = {"data": padded_bytes, "metadata": {"app_id": app_id, "index": index}}
    return dispersal_data


def prepare_get_range_request(app_id, start_index, end_index):
    query_data = {"app_id": app_id, "range": {"start": start_index, "end": end_index}}
    return query_data


class StepsDataAvailability(StepsCommon):

    def find_executor_node(self):
        executor = {}
        for node in self.main_nodes:
            if node.node_type() == NOMOS_EXECUTOR:
                executor = node
        return executor

    @allure.step
    def disperse_data(self, data, app_id, index):
        request = prepare_dispersal_request(data, app_id, index)
        executor = self.find_executor_node()
        try:
            executor.send_dispersal_request(request)
        except Exception as ex:
            assert "Bad Request" in str(ex) or "Internal Server Error" in str(ex)

    @allure.step
    def get_data_range(self, node, app_id, start, end):
        response = []
        query = prepare_get_range_request(app_id, start, end)
        try:
            response = node.send_get_data_range_request(query)
        except Exception as ex:
            assert "Bad Request" in str(ex) or "Internal Server Error" in str(ex)

        return response
