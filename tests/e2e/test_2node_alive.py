from src.env_vars import CFGSYNC, NOMOS, NOMOS_EXECUTOR
from src.node.nomos_node import NomosNode
from src.libs.common import delay


class Test2NodeClAlive:
    def test_cluster_start(self):

        self.node1 = NomosNode(CFGSYNC, "cfgsync")
        self.node2 = NomosNode(NOMOS, "nomos_node_0")
        self.node3 = NomosNode(NOMOS_EXECUTOR, "nomos_node_1")

        self.node1.start()
        self.node2.start()
        self.node3.start()

        delay(60)
