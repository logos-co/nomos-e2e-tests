# -*- coding: utf-8 -*-
import inspect
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.env_vars import CHECK_LOG_ERRORS
from src.libs.custom_logger import get_custom_logger
import os
import pytest
from datetime import datetime
from time import time
from uuid import uuid4
from src.libs.common import attach_allure_file
import src.env_vars as env_vars
from src.data_storage import DS

logger = get_custom_logger(__name__)


def pytest_addoption(parser):
    parser.addoption("--run-with-mod-da-node", action="store_true", default=False, help="Run tests requiring nodes with modified da layer")


def pytest_configure(config):
    config.addinivalue_line("markers", "mod_da_node: Mark test as requiring --run-with-mod-da-node")


def pytest_collection_modifyitems(config, items):
    run_mod_da_node = config.getoption("--run-with-mod-da-node")
    for item in items:
        if "mod_da_node" in item.keywords and not run_mod_da_node:
            item.add_marker(pytest.mark.skip(reason="Requires --run-with-mod-da-node option"))


# See https://docs.pytest.org/en/latest/example/simple.html#making-test-result-information-available-in-fixtures
@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call":
        setattr(item, "rep_call", rep)
        return rep
    return None


@pytest.fixture(scope="session", autouse=True)
def set_allure_env_variables():
    yield
    if os.path.isdir("allure-results") and not os.path.isfile(os.path.join("allure-results", "environment.properties")):
        logger.debug(f"Running fixture teardown: {inspect.currentframe().f_code.co_name}")
        with open(os.path.join("allure-results", "environment.properties"), "w") as outfile:
            for attribute_name in dir(env_vars):
                if attribute_name.isupper():
                    attribute_value = getattr(env_vars, attribute_name)
                    outfile.write(f"{attribute_name}={attribute_value}\n")


@pytest.fixture(scope="function", autouse=True)
def test_id(request):
    # setting up an unique test id to be used where needed
    logger.debug(f"Running fixture setup: {inspect.currentframe().f_code.co_name}")
    request.cls.test_id = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}__{str(uuid4())}"


@pytest.fixture(scope="function", autouse=True)
def test_setup(request, test_id):
    logger.debug(f"Running test: {request.node.name} with id: {request.cls.test_id}")
    yield
    logger.debug(f"Running fixture teardown: {inspect.currentframe().f_code.co_name}")
    for file in glob.glob(os.path.join(env_vars.DOCKER_LOG_DIR, "*")):
        if os.path.getmtime(file) < time() - 3600:
            logger.debug(f"Deleting old log file: {file}")
            try:
                os.remove(file)
            except:
                logger.error("Could not delete file")


@pytest.fixture(scope="function", autouse=True)
def attach_logs_on_fail(request):
    yield
    if env_vars.RUNNING_IN_CI and hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        logger.debug(f"Running fixture teardown: {inspect.currentframe().f_code.co_name}")
        logger.debug("Test failed, attempting to attach logs to the allure reports")
        for file in glob.glob(os.path.join(env_vars.DOCKER_LOG_DIR, "*" + request.cls.test_id + "*")):
            attach_allure_file(file)


def stop_node(node):
    try:
        node.stop()
    except Exception as ex:
        if "No such container" in str(ex):
            logger.error(f"Failed to stop container {node.name()} because of error {ex}")


@pytest.fixture(scope="function", autouse=True)
def close_open_nodes(attach_logs_on_fail):
    DS.nomos_nodes = []
    DS.client_nodes = []
    yield
    logger.debug(f"Running fixture teardown: {inspect.currentframe().f_code.co_name}")
    failed_cleanups = []
    with ThreadPoolExecutor(max_workers=30) as executor:
        node_cleanups = [executor.submit(stop_node, node) for node in DS.nomos_nodes + DS.client_nodes]
        for cleanup in as_completed(node_cleanups):
            try:
                cleanup.result()
            except Exception as ex:
                failed_cleanups.append(ex)

    assert not failed_cleanups, f"Container cleanup failed with {failed_cleanups} !!!"


@pytest.fixture(scope="function", autouse=True)
def check_nomos_log_errors(request):
    yield
    if CHECK_LOG_ERRORS:
        logger.debug(f"Running fixture teardown: {inspect.currentframe().f_code.co_name}")
        for node in DS.nomos_nodes:
            node.check_nomos_log_errors()
