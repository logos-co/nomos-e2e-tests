import allure
from tenacity import retry, stop_after_delay, wait_fixed

from src.libs.custom_logger import get_custom_logger
from src.steps.common import StepsCommon

logger = get_custom_logger(__name__)


class StepsConsensus(StepsCommon):
    @allure.step
    def get_cryptarchia_headers(self, node, from_header_id=None, to_header_id=None, **kwargs):

        timeout_duration = kwargs.get("timeout_duration", 65)
        interval = kwargs.get("interval", 0.1)

        @retry(stop=stop_after_delay(timeout_duration), wait=wait_fixed(interval), reraise=True)
        def get_headers():
            try:
                response = node.send_get_cryptarchia_headers_request(from_header_id, to_header_id)
            except Exception as ex:
                logger.error(f"Exception while retrieving cryptarchia headers: {ex}")
                raise

            return response

        return get_headers()
