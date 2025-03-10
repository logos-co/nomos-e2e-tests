import inspect
import os
import shutil

import pytest

from src.client.nomos_cli import NomosCli
from src.env_vars import CFGSYNC, NOMOS, NOMOS_EXECUTOR
from src.libs.common import delay
from src.libs.custom_logger import get_custom_logger
from src.node.nomos_node import NomosNode

from jinja2 import Template

logger = get_custom_logger(__name__)


def prepare_cluster_config(node_count, subnetwork_size=2):
    cwd = os.getcwd()
    config_dir = "cluster_config"

    with open(f"{cwd}/{config_dir}/cfgsync-template.yaml", "r") as file:
        template_content = file.read()
    template = Template(template_content)

    rendered = template.render(num_hosts=node_count, subnet_size=subnetwork_size)

    with open(f"{cwd}/{config_dir}/cfgsync.yaml", "w") as outfile:
        outfile.write(rendered)


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
        self.client_nodes = []

    @pytest.fixture(scope="function")
    def setup_2_node_cluster(self, request):
        logger.debug(f"Running fixture setup: {inspect.currentframe().f_code.co_name}")

        if hasattr(request, "param"):
            subnet_size = request.param
        else:
            subnet_size = 2

        prepare_cluster_config(2, subnet_size)
        self.node1 = NomosNode(CFGSYNC, "cfgsync")
        self.node2 = NomosNode(NOMOS, "nomos_node_0")
        self.node3 = NomosNode(NOMOS_EXECUTOR, "nomos_node_1")
        self.main_nodes.extend([self.node1, self.node2, self.node3])
        start_nodes(self.main_nodes)

        try:
            ensure_nodes_ready(self.main_nodes[1:])
        except Exception as ex:
            logger.error(f"REST service did not become ready in time: {ex}")
            raise

        delay(5)

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
            ensure_nodes_ready(self.main_nodes[1:])
        except Exception as ex:
            logger.error(f"REST service did not become ready in time: {ex}")
            raise

        delay(5)

    @pytest.fixture(scope="function")
    def setup_client_nodes(self, request):
        logger.debug(f"Running fixture setup: {inspect.currentframe().f_code.co_name}")

        if hasattr(request, "param"):
            num_clients = request.param
        else:
            num_clients = 5

        for i in range(num_clients):
            cli_node = NomosCli(command="client_node")
            cli_node.run()
            self.client_nodes.append(cli_node)
