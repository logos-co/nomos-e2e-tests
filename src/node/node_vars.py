from src.env_vars import NOMOS_IMAGE, NOMOS_MOD_DA_IMAGE, NOMOS_EXECUTOR_MOD_DA_IMAGE, NOMOS_EXECUTOR_MOD_DA_IMAGE_25d781e

nomos_nodes = {
    "nomos_mod_da": {
        "image": NOMOS_MOD_DA_IMAGE,
        "volumes": ["cluster_config:/etc/nomos", "./kzgrs/kzgrs_test_params:/kzgrs_test_params:z"],
        "ports": ["3000/udp", "18080/tcp"],
        "entrypoint": "/etc/nomos/scripts/run_nomos_node_debug.sh",
    },
    "nomos_executor_mod_da": {
        "image": NOMOS_EXECUTOR_MOD_DA_IMAGE,
        "volumes": ["cluster_config:/etc/nomos", "./kzgrs/kzgrs_test_params:/kzgrs_test_params:z"],
        "ports": ["3000/udp", "18080/tcp"],
        "entrypoint": "/etc/nomos/scripts/run_nomos_executor_debug.sh",
    },
    "nomos_executor_mod_da_25d781e": {
        "image": NOMOS_EXECUTOR_MOD_DA_IMAGE_25d781e,
        "volumes": ["cluster_config:/etc/nomos", "./kzgrs/kzgrs_test_params:/kzgrs_test_params:z"],
        "ports": ["3000/udp", "18080/tcp"],
        "entrypoint": "/etc/nomos/scripts/run_nomos_executor_debug.sh",
    },
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
