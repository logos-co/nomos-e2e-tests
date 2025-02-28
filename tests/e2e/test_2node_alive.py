import pytest

from src.libs.custom_logger import get_custom_logger
from src.steps.common import StepsCommon

logger = get_custom_logger(__name__)


class Test2NodeClAlive(StepsCommon):
    @pytest.mark.usefixtures("setup_2_node_cluster")
    def test_cluster_start(self):
        logger.debug("Two node cluster started successfully!")
