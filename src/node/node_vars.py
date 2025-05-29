from src.env_vars import NOMOS_IMAGE

nomos_nodes = {
    "nomos_custom": {
        "image": NOMOS_IMAGE,
        "volumes": ["cluster_config:/etc/nomos", "./kzgrs/kzgrs_test_params:/kzgrs_test_params:z"],
        "ports": ["3000/udp", "18080/tcp"],
        "entrypoint": "/etc/nomos/scripts/run_customized_node.sh",
    },
    "nomos": {
        "image": NOMOS_IMAGE,
        "volumes": ["cluster_config:/etc/nomos", "./kzgrs/kzgrs_test_params:/kzgrs_test_params:z"],
        "ports": ["3000/udp", "18080/tcp"],
        "entrypoint": "/etc/nomos/scripts/run_nomos_node.sh",
    },
    "nomos_executor": {
        "image": NOMOS_IMAGE,
        "volumes": ["cluster_config:/etc/nomos", "./kzgrs/kzgrs_test_params:/kzgrs_test_params:z"],
        "ports": ["3000/udp", "18080/tcp"],
        "entrypoint": "/etc/nomos/scripts/run_nomos_executor.sh",
    },
    "cfgsync": {
        "image": NOMOS_IMAGE,
        "volumes": ["cluster_config:/etc/nomos"],
        "ports": "",
        "entrypoint": "/etc/nomos/scripts/run_cfgsync.sh",
    },
}
