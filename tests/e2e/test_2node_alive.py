from src.env_vars import CFGSYNC, NOMOS, NOMOS_EXECUTOR
from src.libs.custom_logger import get_custom_logger
from src.node.nomos_node import NomosNode
from src.libs.common import delay

logger = get_custom_logger(__name__)


class Test2NodeClAlive:
    def test_cluster_start(self):

        self.node1 = NomosNode(CFGSYNC, "cfgsync")
        self.node2 = NomosNode(NOMOS, "nomos_node_0")
        self.node3 = NomosNode(NOMOS_EXECUTOR, "nomos_node_1")

        self.node1.start()
        self.node2.start()
        self.node3.start()

        self.node1.ensure_ready()
        try:
            self.node2.ensure_ready()
            self.node3.ensure_ready()
        except Exception as ex:
            logger.error(f"REST service did not become ready in time: {ex}")
            raise

        delay(60)
