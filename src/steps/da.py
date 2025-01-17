import allure

from src.steps.common import StepsCommon


def prepare_dispersal_data(data):
    data_bytes = data.encode("utf-8")
    dispersal_data = {"data": list(data_bytes), "metadata": {"app_id": [1] + [0] * 31, "index": 0}}
    return dispersal_data


class StepsDataAvailability(StepsCommon):

    @allure.step
    def disperse_data(self, data):
        dispersal_data = prepare_dispersal_data(data)
        try:
            self.node3.send_dispersal_request(dispersal_data)
        except Exception as ex:
            assert "Bad Request" in str(ex) or "Internal Server Error" in str(ex)
