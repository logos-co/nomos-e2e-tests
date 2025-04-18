import math
import random
import string
import uuid
from datetime import datetime
from time import sleep

from faker import Faker
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
    return to_byte_list(n, 8)


def to_app_id(n: int) -> list:
    return to_byte_list(n, 32)


def to_blob_id(n: int) -> list:
    return to_byte_list(n, 32)


def to_header_id(n: int):
    if n < 0:
        raise ValueError("Input must be an unsigned integer (non-negative)")

    return n.to_bytes(32, byteorder="big").hex()


def to_byte_list(n: int, l: int) -> list:
    if n < 0:
        raise ValueError("Input must be an unsigned integer (non-negative)")
    if l < 1:
        raise ValueError("Length must be an unsigned integer greater than 0")

    return list(n.to_bytes(l, byteorder="big"))


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


def generate_text_data(target_size):
    faker = Faker()
    text_data = faker.text(max_nb_chars=math.floor(target_size * 1.2))  # 20% more than target size
    text_data = " ".join(text_data.splitlines())  # remove newlines

    while len(text_data.encode("utf-8")) > target_size:  # trim to exact size
        text_data = text_data[:-1]

    logger.debug(f"Raw data size: {len(text_data.encode("utf-8"))}\n\t{text_data}")

    return text_data


def add_padding(orig_bytes):
    """
    Pads a list of bytes (integers in [0..255]) using a PKCS#7-like scheme:
    - The value of each padded byte is the number of bytes padded.
    - If the original data is already a multiple of the block size,
      an additional full block of bytes (each the block size) is added.
    """
    block_size = 31
    original_len = len(orig_bytes)
    padding_needed = block_size - (original_len % block_size)
    # If the data is already a multiple of block_size, add a full block of padding
    if padding_needed == 0:
        padding_needed = block_size

    # Each padded byte will be equal to padding_needed
    padded_bytes = orig_bytes + [padding_needed] * padding_needed
    return padded_bytes


def remove_padding(padded_bytes):
    """
    Removes PKCS#7-like padding from a list of bytes.
    Raises:
        ValueError: If the padding is incorrect.
    Returns:
        The original list of bytes without padding.
    """
    if not padded_bytes:
        raise ValueError("The input is empty, cannot remove padding.")

    padding_len = padded_bytes[-1]

    if padding_len < 1 or padding_len > 31:
        raise ValueError("Invalid padding length.")

    if padded_bytes[-padding_len:] != [padding_len] * padding_len:
        raise ValueError("Invalid padding bytes.")

    return padded_bytes[:-padding_len]
