import io
import json
import tarfile

import pytest
from ruamel.yaml import YAML

from src.client.nomos_cli import NomosCli
from src.env_vars import CONSENSUS_SLOT_TIME, NOMOS_CUSTOM
from src.libs.common import delay, to_app_id, to_index
from src.libs.custom_logger import get_custom_logger
from src.node.nomos_node import NomosNode
from src.steps.da import StepsDataAvailability
from src.test_data import DATA_TO_DISPERSE

logger = get_custom_logger(__name__)


def modify_key_value(file_path, yaml_key_path):
    yaml = YAML()
    yaml.preserve_quotes = True

    with open(file_path, "r") as f:
        data = yaml.load(f)

    keys = yaml_key_path.split(".")
    ref = data
    for key in keys[:-1]:
        if key not in ref:
            raise KeyError(f"Key '{key}' not found in path '{'.'.join(keys)}'")
        ref = ref[key]

    final_key = keys[-1]
    if final_key not in ref:
        raise KeyError(f"Key '{final_key}' not found in path '{'.'.join(keys)}'")

    old_value = ref[final_key]
    # Swap last two characters
    ref[final_key] = old_value[:-2] + old_value[-1] + old_value[-2]

    with open(file_path, "w") as f:
        yaml.dump(data, f)


class TestDataConfidentiality(StepsDataAvailability):
    main_nodes = []

    @pytest.mark.usefixtures("setup_2_node_cluster")
    def test_unauthorized_node_cannot_receive_dispersed_data(self):
        self.disperse_data(DATA_TO_DISPERSE[1], to_app_id(1), to_index(0))
        delay(CONSENSUS_SLOT_TIME)
        rcv_data = self.get_data_range(self.node2, to_app_id(1), to_index(0), to_index(5))
        rcv_data_json = json.dumps(rcv_data)

        decoded_data = NomosCli(command="reconstruct").run(input_values=[rcv_data_json], decode_only=True)

        assert DATA_TO_DISPERSE[1] == decoded_data, "Retrieved data are not same with original data"

        # Copy the config file from first node
        stream, _stat = self.node2.get_archive("/config.yaml")

        # Join stream into bytes and load into a memory buffer
        tar_bytes = io.BytesIO(b"".join(stream))

        # Extract and write only the actual text file
        with tarfile.open(fileobj=tar_bytes) as tar:
            member = tar.getmembers()[0]
            file_obj = tar.extractfile(member)
            if file_obj:
                with open("./cluster_config/config.yaml", "wb") as f:
                    f.write(file_obj.read())

        self.node2.stop()

        # Change the private key -> PeerId of the nomos_node_0. This would create a stranger to existing membership list.
        for yaml_key_path in ["network.backend.node_key", "blend.backend.node_key", "da_network.backend.node_key"]:
            modify_key_value("./cluster_config/config.yaml", yaml_key_path)

        # Start new node with the same hostname and configuration as first node
        self.nodeX = NomosNode(NOMOS_CUSTOM, "nomos_node_0")
        self.nodeX.start()

        try:
            self.nodeX.ensure_ready()
        except Exception as ex:
            logger.error(f"REST service did not become ready in time: {ex}")
            raise

        # Confirm new node haven't received any dispersed data as it is not on membership list.
        self.disperse_data(DATA_TO_DISPERSE[2], to_app_id(2), to_index(0))
        delay(CONSENSUS_SLOT_TIME)
        try:
            _rcv_data = self.get_data_range(self.nodeX, to_app_id(2), to_index(0), to_index(5))
        except AssertionError as ae:
            assert "Get data range response is empty" in str(ae), "Get data range response should be empty"
