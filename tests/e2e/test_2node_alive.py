import pytest

from src.env_vars import CFGSYNC, NOMOS, NOMOS_EXECUTOR
from src.libs.custom_logger import get_custom_logger
from src.node.nomos_node import NomosNode
from src.steps.common import StepsCommon

logger = get_custom_logger(__name__)


class Test2NodeClAlive(StepsCommon):
    @pytest.mark.usefixtures("setup_main_nodes")
    def test_cluster_start(self):
        logger.debug("Two node cluster started successfully!")
