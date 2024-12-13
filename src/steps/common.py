import inspect

import pytest

from src.env_vars import NODE_1, NODE_2
from src.libs.custom_logger import get_custom_logger
from src.node.nomos_node import NomosNode

logger = get_custom_logger(__name__)


class StepsCommon:
    @pytest.fixture(scope="function")
    def setup_main_nodes(self, request):
        logger.debug(f"Running fixture setup: {inspect.currentframe().f_code.co_name}")
        self.node1 = NomosNode(NODE_1, f"node1_{request.cls.test_id}")
        self.node1.start()
        self.node2 = NomosNode(NODE_2, f"node2_{request.cls.test_id}")
        self.node2.start()
        self.main_nodes.extend([self.node1, self.node2])
