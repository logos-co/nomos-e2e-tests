from src.env_vars import CFGSYNC, NODE_1, NODE_2
from src.node.nomos_node import NomosNode


class Test2NodeClAlive:
    def test_cluster_start(self):

        self.node1 = NomosNode(CFGSYNC, f"node1_{1}")
        self.node2 = NomosNode(NODE_1, f"node2_{2}")
        self.node3 = NomosNode(NODE_2, f"node3_{3}")

        self.node1.start()
        self.node2.start()
        self.node3.start()
