import allure
from tenacity import retry, stop_after_delay, wait_fixed

from src.libs.custom_logger import get_custom_logger
from src.steps.common import StepsCommon

logger = get_custom_logger(__name__)


def prepare_add_blob_info_request(blob_id, app_id, index):
    blob_info = {"id": blob_id, "metadata": {"app_id": app_id, "index": index}}
    return blob_info


class StepsMempool(StepsCommon):
    @allure.step
    def add_dispersed_blob_info(self, node, blob_id, app_id, index, **kwargs):

        timeout_duration = kwargs.get("timeout_duration", 65)
        interval = kwargs.get("interval", 0.1)

        data = prepare_add_blob_info_request(blob_id, app_id, index)

        @retry(stop=stop_after_delay(timeout_duration), wait=wait_fixed(interval), reraise=True)
        def add_blob_info():
            try:
                response = node.send_add_blob_info_request(data)
            except Exception as ex:
                logger.error(f"Exception while adding blob info to mempool: {ex}")
                raise

            return response

        return add_blob_info()
