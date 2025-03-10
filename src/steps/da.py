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
    def disperse_data(self, data, app_id, index, client_node=None, timeout_duration=65, utf8=True, padding=True, send_invalid=False):
        @retry(stop=stop_after_delay(timeout_duration), wait=wait_fixed(0.1), reraise=True)
        def disperse(my_self=self):
            response = []
            request = prepare_dispersal_request(data, app_id, index, utf8=utf8, padding=padding)
            executor = my_self.find_executor_node()

            try:
                if client_node is None:
                    response = executor.send_dispersal_request(request)
                else:
                    if send_invalid:
                        client_node.set_invalid_rest_api()
                    else:
                        client_node.set_rest_api()
                    response = client_node.send_dispersal_request(request)
            except Exception as ex:
                assert "Bad Request" in str(ex) or "Internal Server Error" in str(ex)

            assert hasattr(response, "status_code"), "Missing status_code"
            assert response.status_code in (200, 429), "Unexpected status code"

            return response

        return disperse()

    @allure.step
    def get_data_range(self, node, app_id, start, end, client_node=None, timeout_duration=45, send_invalid=False):
        @retry(stop=stop_after_delay(timeout_duration), wait=wait_fixed(0.1), reraise=True)
        def get_range():
            response = []
            query = prepare_get_range_request(app_id, start, end)
            try:
                if client_node is None:
                    response = node.send_get_data_range_request(query)
                else:
                    if send_invalid:
                        client_node.set_invalid_rest_api()
                    else:
                        client_node.set_rest_api()
                    response = client_node.send_get_data_range_request(query)
            except Exception as ex:
                assert "Bad Request" in str(ex) or "Internal Server Error" in str(ex)

            assert response_contains_data(response), "Get data range response is empty"

            return response

        return get_range()
