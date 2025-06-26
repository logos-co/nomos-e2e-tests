from src.env_vars import (
    NOMOS_IMAGE,
    NOMOS_MOD_DA_IMAGE_d8bbc46,
    NOMOS_EXECUTOR_MOD_DA_IMAGE_d19a1f3,
    NOMOS_EXECUTOR_MOD_DA_IMAGE_7f54114,
    NOMOS_EXECUTOR_MOD_DA_IMAGE_4a58376,
)

nomos_nodes = {
    "nomos_mod_da_d8bbc46": {
        "image": NOMOS_MOD_DA_IMAGE_d8bbc46,
        "volumes": ["cluster_config:/etc/nomos", "./kzgrs/kzgrs_test_params:/kzgrs_test_params:z"],
        "ports": ["3000/udp", "18080/tcp"],
        "entrypoint": "/etc/nomos/scripts/run_nomos_node_debug.sh",
    },
    "nomos_executor_mod_da_d19a1f3": {
        "image": NOMOS_EXECUTOR_MOD_DA_IMAGE_d19a1f3,
        "volumes": ["cluster_config:/etc/nomos", "./kzgrs/kzgrs_test_params:/kzgrs_test_params:z"],
        "ports": ["3000/udp", "18080/tcp"],
        "entrypoint": "/etc/nomos/scripts/run_nomos_executor_debug.sh",
    },
    "nomos_executor_mod_da_7f54114": {
        "image": NOMOS_EXECUTOR_MOD_DA_IMAGE_7f54114,
        "volumes": ["cluster_config:/etc/nomos", "./kzgrs/kzgrs_test_params:/kzgrs_test_params:z"],
        "ports": ["3000/udp", "18080/tcp"],
        "entrypoint": "/etc/nomos/scripts/run_nomos_executor_debug.sh",
    },
    "nomos_executor_mod_da_4a58376": {
        "image": NOMOS_EXECUTOR_MOD_DA_IMAGE_4a58376,
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
