from urllib.parse import quote

import allure
from tenacity import retry, stop_after_delay, wait_fixed

from src.libs.custom_logger import get_custom_logger
from src.steps.common import StepsCommon

logger = get_custom_logger(__name__)


def prepare_get_storage_block_request(header_id):
    query_data = f"{header_id}"
    return query_data


class StepsStorage(StepsCommon):
    @allure.step
    def get_storage_block(self, node, header_id, **kwargs):

        timeout_duration = kwargs.get("timeout_duration", 65)
        interval = kwargs.get("interval", 0.1)

        query = prepare_get_storage_block_request(header_id)

        @retry(stop=stop_after_delay(timeout_duration), wait=wait_fixed(interval), reraise=True)
        def get_block():
            try:
                response = node.send_get_storage_block_request(query)
            except Exception as ex:
                logger.error(f"Exception while retrieving storage block: {ex}")
                raise

            return response

        return get_block()
