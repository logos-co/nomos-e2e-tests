import allure
from tenacity import retry, stop_after_delay, wait_fixed

from src.env_vars import NOMOS_EXECUTOR
from src.libs.common import add_padding
from src.libs.custom_logger import get_custom_logger
from src.steps.common import StepsCommon

logger = get_custom_logger(__name__)


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


def prepare_get_shares_commitments_request(blob_id):
    query_data = {"blob_id": blob_id}
    return query_data


def response_contains_data(response):
    if response is None:
        return False

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
    def disperse_data(self, data, app_id, index, client_node=None, **kwargs):

        timeout_duration = kwargs.get("timeout_duration", 65)
        utf8 = kwargs.get("utf8", True)
        padding = kwargs.get("padding", True)
        send_invalid = kwargs.get("send_invalid", False)

        request = prepare_dispersal_request(data, app_id, index, utf8=utf8, padding=padding)

        @retry(stop=stop_after_delay(timeout_duration), wait=wait_fixed(0.1), reraise=True)
        def disperse(my_self=self):
            try:
                if client_node is None:
                    executor = my_self.find_executor_node()
                    response = executor.send_dispersal_request(request)
                else:
                    response = client_node.send_dispersal_request(request, send_invalid=send_invalid)

            except Exception as ex:
                logger.error(f"Exception while dispersing data: {ex}")
                raise

            assert hasattr(response, "status_code"), "Missing status_code"

            return response

        return disperse()

    @allure.step
    def get_data_range(self, node, app_id, start, end, client_node=None, **kwargs):

        timeout_duration = kwargs.get("timeout_duration", 65)
        interval = kwargs.get("interval", 0.1)
        send_invalid = kwargs.get("send_invalid", False)

        query = prepare_get_range_request(app_id, start, end)

        @retry(stop=stop_after_delay(timeout_duration), wait=wait_fixed(interval), reraise=True)
        def get_range():
            try:
                if client_node is None:
                    response = node.send_get_data_range_request(query)
                else:
                    response = client_node.send_get_data_range_request(query, send_invalid=send_invalid)
            except Exception as ex:
                logger.error(f"Exception while retrieving data: {ex}")
                raise

            assert response_contains_data(response), "Get data range response is empty"

            return response

        return get_range()

    @allure.step
    def get_shares_commitments(self, node, blob_id, **kwargs):

        timeout_duration = kwargs.get("timeout_duration", 65)
        interval = kwargs.get("interval", 0.1)

        query = prepare_get_shares_commitments_request(blob_id)

        @retry(stop=stop_after_delay(timeout_duration), wait=wait_fixed(interval), reraise=True)
        def get_commitments():
            try:
                response = node.send_get_commitments_request(query)
            except Exception as ex:
                logger.error(f"Exception while retrieving commitments: {ex}")
                raise

            return response

        return get_commitments()

    @allure.step
    def add_publish_share(self, node, da_share, **kwargs):

        timeout_duration = kwargs.get("timeout_duration", 65)
        interval = kwargs.get("interval", 0.1)

        @retry(stop=stop_after_delay(timeout_duration), wait=wait_fixed(interval), reraise=True)
        def add_share():
            try:
                response = node.send_add_share_request(da_share)
            except Exception as ex:
                logger.error(f"Exception while adding share: {ex}")
                raise

            return response

        return add_share()
