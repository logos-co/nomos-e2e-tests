import json

import allure

from src.env_vars import NOMOS_EXECUTOR
from src.steps.common import StepsCommon


def prepare_dispersal_request(data, app_id, index):
    data_bytes = data.encode("utf-8")
    dispersal_data = {"data": list(data_bytes), "metadata": {"app_id": app_id, "index": index}}
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
    def get_data_range(self, app_id, start, end):
        response = []
        query = prepare_get_range_request(app_id, start, end)
        try:
            response = self.node2.send_get_data_range_request(query)
        except Exception as ex:
            assert "Bad Request" in str(ex) or "Internal Server Error" in str(ex)

        return response
