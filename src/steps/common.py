import inspect
import os
import shutil

import pytest

from src.env_vars import CFGSYNC, NOMOS, NOMOS_EXECUTOR
from src.libs.custom_logger import get_custom_logger
from src.node.nomos_node import NomosNode

logger = get_custom_logger(__name__)


def prepare_cluster_config(node_count):
    cwd = os.getcwd()
    config_dir = "cluster_config"
    src = f"{cwd}/{config_dir}/cfgsync-{node_count}node.yaml"
    dst = f"{cwd}/{config_dir}/cfgsync.yaml"
    shutil.copyfile(src, dst)


def start_nodes(nodes):
    for node in nodes:
        node.start()


def ensure_nodes_ready(nodes):
    for node in nodes:
        node.ensure_ready()


class StepsCommon:
    @pytest.fixture(scope="function", autouse=True)
    def cluster_setup(self):
        logger.debug(f"Running fixture setup: {inspect.currentframe().f_code.co_name}")
        self.main_nodes = []

    @pytest.fixture(scope="function")
    def setup_2_node_cluster(self, request):
        logger.debug(f"Running fixture setup: {inspect.currentframe().f_code.co_name}")
        prepare_cluster_config(2)
        self.node1 = NomosNode(CFGSYNC, "cfgsync")
        self.node2 = NomosNode(NOMOS, "nomos_node_0")
        self.node3 = NomosNode(NOMOS_EXECUTOR, "nomos_node_1")
        self.main_nodes.extend([self.node1, self.node2, self.node3])
        start_nodes(self.main_nodes)

        try:
            ensure_nodes_ready(self.main_nodes[2:])
        except Exception as ex:
            logger.error(f"REST service did not become ready in time: {ex}")
            raise

    @pytest.fixture(scope="function")
    def setup_4_node_cluster(self, request):
        logger.debug(f"Running fixture setup: {inspect.currentframe().f_code.co_name}")
        prepare_cluster_config(4)
        self.node1 = NomosNode(CFGSYNC, "cfgsync")
        self.node2 = NomosNode(NOMOS, "nomos_node_0")
        self.node3 = NomosNode(NOMOS, "nomos_node_1")
        self.node4 = NomosNode(NOMOS, "nomos_node_2")
        self.node5 = NomosNode(NOMOS_EXECUTOR, "nomos_node_3")
        self.main_nodes.extend([self.node1, self.node2, self.node3, self.node4, self.node5])
        start_nodes(self.main_nodes)

        try:
            ensure_nodes_ready(self.main_nodes[2:])
        except Exception as ex:
            logger.error(f"REST service did not become ready in time: {ex}")
            raise
