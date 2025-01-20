import json

import allure

from src.steps.common import StepsCommon


def prepare_dispersal_request(data, app_id, index):
    data_bytes = data.encode("utf-8")
    dispersal_data = {"data": list(data_bytes), "metadata": {"app_id": app_id, "index": index}}
    return dispersal_data


def prepare_get_range_request(app_id, start_index, end_index):
    query_data = {"app_id": app_id, "range": {"start": start_index, "end": end_index}}
    return query_data


class StepsDataAvailability(StepsCommon):

    @allure.step
    def disperse_data(self, data, app_id, index):
        request = prepare_dispersal_request(data, app_id, index)
        try:
            self.node3.send_dispersal_request(request)
        except Exception as ex:
            assert "Bad Request" in str(ex) or "Internal Server Error" in str(ex)

    @allure.step
    def get_data_range(self, app_id, start, end):
        response_bytes = []
        query = prepare_get_range_request(app_id, start, end)
        try:
            response_bytes = self.node2.send_get_data_range_request(query)
        except Exception as ex:
            assert "Bad Request" in str(ex) or "Internal Server Error" in str(ex)

        # Extract data ss string for each index in the received order
        response = response_bytes.decode("utf-8")
        parsed_data = json.loads(response)
        return [item[1] for item in parsed_data]
