import random
import string

from src.api_clients.rest import REST
from src.libs.common import generate_random_bytes
from src.libs.custom_logger import get_custom_logger
import json

logger = get_custom_logger(__name__)


def alter_dispersal_data(data):

    # Add random bytes to data and break padding
    def alter_data_content():
        random_n = random.randint(1, 31)
        data["data"].extend(list(generate_random_bytes(random_n)))

    # Change structure and content for metadata
    def alter_metadata():
        random_n = random.randint(7, 32)
        data["metadata"] = list(generate_random_bytes(random_n))

    # Add random property to the data object with random list content
    def add_random_property():
        random_k = random.randint(1, 16)
        random_n = random.randint(7, 64)
        random_str = "".join(random.choices(string.printable, k=random_k))
        data[random_str] = list(generate_random_bytes(random_n))

    choice = random.choice([alter_data_content, alter_metadata, add_random_property])
    logger.debug(f"Data for dispersal request has been altered with: {choice.__name__}")

    choice()

    return data


def alter_get_range_query(query):

    # Swap range high with range low
    def swap_range():
        end = query["range"]["end"]
        query["range"]["end"] = query["range"]["start"]
        query["range"]["start"] = end

    # Change app id
    def alter_app_id():
        random_n = random.randint(8, 33)
        query["app_id"] = list(generate_random_bytes(random_n))

    choice = random.choice([swap_range, alter_app_id])
    logger.debug(f"Get-range query has been altered with: {choice.__name__}")

    choice()

    return query


class InvalidRest(REST):
    def __init__(self, rest_port):
        super().__init__(rest_port)

    def send_dispersal_request(self, data):
        data = alter_dispersal_data(data)
        response = self.rest_call("post", "disperse-data", json.dumps(data))
        return response

    def send_get_range(self, query):
        query = alter_get_range_query(query)
        response = self.rest_call("post", "da/get-range", json.dumps(query))
        return response.json()
