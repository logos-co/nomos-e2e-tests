import allure
from tenacity import retry, stop_after_delay, wait_fixed

from src.env_vars import NOMOS_EXECUTOR
from src.libs.custom_logger import get_custom_logger
from src.steps.common import StepsCommon

logger = get_custom_logger(__name__)


def add_padding(orig_bytes):
    """
    Pads a list of bytes (integers in [0..255]) using a PKCS#7-like scheme:
    - The value of each padded byte is the number of bytes padded.
    - If the original data is already a multiple of the block size,
      an additional full block of bytes (each the block size) is added.
    """
    block_size = 31
    original_len = len(orig_bytes)
    padding_needed = block_size - (original_len % block_size)
    # If the data is already a multiple of block_size, add a full block of padding
    if padding_needed == 0:
        padding_needed = block_size

    # Each padded byte will be equal to padding_needed
    padded_bytes = orig_bytes + [padding_needed] * padding_needed
    return padded_bytes


def remove_padding(padded_bytes):
    """
    Removes PKCS#7-like padding from a list of bytes.
    Raises:
        ValueError: If the padding is incorrect.
    Returns:
        The original list of bytes without padding.
    """
    if not padded_bytes:
        raise ValueError("The input is empty, cannot remove padding.")

    padding_len = padded_bytes[-1]

    if padding_len < 1 or padding_len > 31:
        raise ValueError("Invalid padding length.")

    if padded_bytes[-padding_len:] != [padding_len] * padding_len:
        raise ValueError("Invalid padding bytes.")

    return padded_bytes[:-padding_len]


def prepare_dispersal_request(data, app_id, index, utf8=True, padding=True):
    if utf8:
        data_bytes = data.encode("utf-8")
    else:
        data_bytes = bytes(data)

    data_list = list(data_bytes)
    if padding:
        data_list = add_padding(data_list)

    dispersal_data = {"data": data_list, "metadata": {"app_id": app_id, "index": index}}
    return dispersal_data


def prepare_get_range_request(app_id, start_index, end_index):
    query_data = {"app_id": app_id, "range": {"start": start_index, "end": end_index}}
    return query_data


def response_contains_data(response):
    for index, blobs in response:
        if len(blobs) != 0:
            return True

    return False


class StepsDataAvailability(StepsCommon):
    def find_executor_node(self):
        executor = {}
        for node in self.main_nodes:
            if node.node_type() == NOMOS_EXECUTOR:
                executor = node
        return executor

    @allure.step
    @retry(stop=stop_after_delay(65), wait=wait_fixed(1), reraise=True)
    def disperse_data(self, data, app_id, index, utf8=True, padding=True):
        response = []
        request = prepare_dispersal_request(data, app_id, index, utf8=utf8, padding=padding)
        executor = self.find_executor_node()
        try:
            response = executor.send_dispersal_request(request)
        except Exception as ex:
            assert "Bad Request" in str(ex) or "Internal Server Error" in str(ex)

        assert response.status_code == 200, "Send dispersal finished with unexpected response code"

    @allure.step
    @retry(stop=stop_after_delay(45), wait=wait_fixed(1), reraise=True)
    def get_data_range(self, node, app_id, start, end):
        response = []
        query = prepare_get_range_request(app_id, start, end)
        try:
            response = node.send_get_data_range_request(query)
        except Exception as ex:
            assert "Bad Request" in str(ex) or "Internal Server Error" in str(ex)

        assert response_contains_data(response), "Get data range response is empty"

        return response
