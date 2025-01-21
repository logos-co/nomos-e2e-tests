import inspect

import pytest

from src.env_vars import NODE_1, NODE_2, CFGSYNC, NOMOS, NOMOS_EXECUTOR
from src.libs.custom_logger import get_custom_logger
from src.node.nomos_node import NomosNode

logger = get_custom_logger(__name__)


class StepsCommon:
    @pytest.fixture(scope="function", autouse=True)
    def cluster_setup(self):
        logger.debug(f"Running fixture setup: {inspect.currentframe().f_code.co_name}")
        self.main_nodes = []

    @pytest.fixture(scope="function")
    def setup_2_node_cluster(self, request):
        logger.debug(f"Running fixture setup: {inspect.currentframe().f_code.co_name}")
        self.node1 = NomosNode(CFGSYNC, "cfgsync")
        self.node2 = NomosNode(NOMOS, "nomos_node_0")
        self.node3 = NomosNode(NOMOS_EXECUTOR, "nomos_node_1")
        self.node1.start()
        self.node2.start()
        self.node3.start()
        self.main_nodes.extend([self.node1, self.node2, self.node3])

        try:
            self.node2.ensure_ready()
            self.node3.ensure_ready()
        except Exception as ex:
            logger.error(f"REST service did not become ready in time: {ex}")
            raise

    @pytest.fixture(scope="function")
    def setup_5_node_cluster(self, request):
        logger.debug(f"Running fixture setup: {inspect.currentframe().f_code.co_name}")
        self.node1 = NomosNode(CFGSYNC, "cfgsync")
        self.node2 = NomosNode(NOMOS, "nomos_node_0")
        self.node3 = NomosNode(NOMOS, "nomos_node_1")
        self.node4 = NomosNode(NOMOS, "nomos_node_2")
        self.node5 = NomosNode(NOMOS, "nomos_node_3")
        self.node6 = NomosNode(NOMOS_EXECUTOR, "nomos_node_4")
        self.node1.start()
        self.node2.start()
        self.node3.start()
        self.node4.start()
        self.node5.start()
        self.node6.start()
        self.main_nodes.extend([self.node1, self.node2, self.node3, self.node4, self.node5, self.node6])

        try:
            self.node2.ensure_ready()
            self.node3.ensure_ready()
            self.node4.ensure_ready()
            self.node5.ensure_ready()
            self.node6.ensure_ready()
        except Exception as ex:
            logger.error(f"REST service did not become ready in time: {ex}")
            raise
