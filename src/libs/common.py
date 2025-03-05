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


def to_index(n: int) -> list:
    if n < 0:
        raise ValueError("Input must be an unsigned integer (non-negative)")
    return list(n.to_bytes(8, byteorder="big"))


def to_app_id(n: int) -> list:
    if n < 0:
        raise ValueError("Input must be an unsigned integer (non-negative)")
    return list(n.to_bytes(32, byteorder="big"))


def random_divide_k(n, k):
    if n < k:
        raise ValueError(f"n={n} must be at least k={k} to split into {k} parts")
    cuts = sorted(random.sample(range(1, n), k - 1))
    parts = [cuts[0]] + [cuts[i] - cuts[i - 1] for i in range(1, len(cuts))] + [n - cuts[-1]]
    return parts


def generate_random_bytes(n=31):
    if n < 0:
        raise ValueError("Input must be an unsigned integer (non-negative)")
    return os.urandom(n)
