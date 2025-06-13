import inspect
import os

import pytest

from src.client.proxy_client import ProxyClient
from src.env_vars import CFGSYNC, NOMOS, NOMOS_EXECUTOR, CONSENSUS_SLOT_TIME, NOMOS_MOD_DA, NOMOS_EXECUTOR_MOD_DA
from src.libs.common import delay
from src.libs.custom_logger import get_custom_logger
from src.node.nomos_node import NomosNode

from jinja2 import Template

logger = get_custom_logger(__name__)


def prepare_cluster_config(node_count, subnetwork_size=2, dispersal_factor=2, min_dispersal_peers=1):
    cwd = os.getcwd()
    config_dir = "cluster_config"

    with open(f"{cwd}/{config_dir}/cfgsync-template.yaml", "r") as file:
        template_content = file.read()
    template = Template(template_content)

    rendered = template.render(
        num_hosts=node_count, subnet_size=subnetwork_size, dispersal_factor=dispersal_factor, min_dispersal_peers=min_dispersal_peers
    )

    with open(f"{cwd}/{config_dir}/cfgsync.yaml", "w") as outfile:
        outfile.write(rendered)


def start_nodes(nodes):
    for node in nodes:
        node.start()


def ensure_nodes_ready(nodes):
    for node in nodes:
        node.ensure_ready()


def get_param_or_default(request, param_name, default_value):
    return request.param.get(param_name, default_value) if hasattr(request, "param") else default_value


class StepsCommon:
    @pytest.fixture(scope="function", autouse=True)
    def cluster_setup(self):
        logger.debug(f"Running fixture setup: {inspect.currentframe().f_code.co_name}")
        self.main_nodes = []
        self.client_nodes = []

    @pytest.fixture(scope="function")
    def setup_2_node_cluster(self, request):
        logger.debug(f"Running fixture setup: {inspect.currentframe().f_code.co_name}")

        subnet_size = get_param_or_default(request, "subnet_size", 2)
        dispersal_factor = get_param_or_default(request, "dispersal_factor", 2)
        min_dispersal_peers = get_param_or_default(request, "min_dispersal_peers", 1)
        prepare_cluster_config(2, subnet_size, dispersal_factor, min_dispersal_peers)

        self.node1 = NomosNode(CFGSYNC, "cfgsync")
        self.node2 = NomosNode(NOMOS, "nomos_node_0")
        self.node3 = NomosNode(NOMOS_EXECUTOR, "nomos_node_1")
        self.main_nodes.extend([self.node1, self.node2, self.node3])
        start_nodes(self.main_nodes)
        ensure_nodes_ready(self.main_nodes[1:])

        delay(CONSENSUS_SLOT_TIME)

    @pytest.fixture(scope="function")
    def setup_4_node_cluster(self, request):
        logger.debug(f"Running fixture setup: {inspect.currentframe().f_code.co_name}")

        subnet_size = get_param_or_default(request, "subnet_size", 4)
        dispersal_factor = get_param_or_default(request, "dispersal_factor", 2)
        min_dispersal_peers = get_param_or_default(request, "min_dispersal_peers", 4)
        prepare_cluster_config(4, subnet_size, dispersal_factor, min_dispersal_peers)

        self.node1 = NomosNode(CFGSYNC, "cfgsync")
        self.node2 = NomosNode(NOMOS, "nomos_node_0")
        self.node3 = NomosNode(NOMOS, "nomos_node_1")
        self.node4 = NomosNode(NOMOS, "nomos_node_2")
        self.node5 = NomosNode(NOMOS_EXECUTOR, "nomos_node_3")
        self.main_nodes.extend([self.node1, self.node2, self.node3, self.node4, self.node5])
        start_nodes(self.main_nodes)
        ensure_nodes_ready(self.main_nodes[1:])

        delay(CONSENSUS_SLOT_TIME)

    @pytest.fixture(scope="function")
    def setup_proxy_clients(self, request):
        logger.debug(f"Running fixture setup: {inspect.currentframe().f_code.co_name}")

        assert len(self.main_nodes) == 3, "There should be two Nomos nodes running already"

        if hasattr(request, "param"):
            num_clients = request.param
        else:
            num_clients = 10

        assert num_clients % 2 == 0, "num_clients must be an even number"

        # Every even proxy client for get-range, every odd for dispersal
        for i in range(num_clients):
            proxy_client = ProxyClient()
            default_target = [f"http://{self.main_nodes[1 + i % 2].name()}:18080"]
            proxy_client.run(input_values=default_target)
            self.client_nodes.append(proxy_client)

    @pytest.fixture(params=["setup_2_node_cluster", "setup_4_node_cluster"])
    def setup_cluster_variant(self, request):
        return request.getfixturevalue(request.param)

    @pytest.fixture(scope="function")
    def setup_2_node_mod_da_cluster(self, request):
        logger.debug(f"Running fixture setup: {inspect.currentframe().f_code.co_name}")

        subnet_size = get_param_or_default(request, "subnet_size", 2)
        dispersal_factor = get_param_or_default(request, "dispersal_factor", 2)
        min_dispersal_peers = get_param_or_default(request, "min_dispersal_peers", 1)
        prepare_cluster_config(2, subnet_size, dispersal_factor, min_dispersal_peers)

        self.node1 = NomosNode(CFGSYNC, "cfgsync")
        self.node2 = NomosNode(NOMOS_MOD_DA, "nomos_node_0")
        self.node3 = NomosNode(NOMOS_EXECUTOR_MOD_DA, "nomos_node_1")
        self.main_nodes.extend([self.node1, self.node2, self.node3])
        start_nodes(self.main_nodes)
        ensure_nodes_ready(self.main_nodes[1:])

        delay(CONSENSUS_SLOT_TIME)
