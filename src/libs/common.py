import random
import string
import uuid
from datetime import datetime
from time import sleep
from src.libs.custom_logger import get_custom_logger
import os
import allure

logger = get_custom_logger(__name__)


def attach_allure_file(file):
    logger.debug(f"Attaching file {file}")
    allure.attach.file(file, name=os.path.basename(file), attachment_type=allure.attachment_type.TEXT)


def delay(num_seconds):
    logger.debug(f"Sleeping for {num_seconds} seconds")
    sleep(num_seconds)


def gen_step_id():
    return f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}__{str(uuid.uuid4())}"


def generate_log_prefix():
    return "".join(random.choices(string.ascii_lowercase, k=4))
