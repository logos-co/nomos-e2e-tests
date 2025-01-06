nomos_nodes = {
    "nomos": {
        "image": "ghcr.io/logos-co/nomos-node:testnet",
        "volumes": ["./cl_config:/etc/nomos", "./kzgrs/kzgrs_test_params.bin:/kzgrs_test_params:z"],
        "ports": ["3000/udp", "18080/tcp"],
        "entrypoint": "/etc/nomos/scripts/run_nomos_node.sh",
    },
    "nomos_executor": {
        "image": "ghcr.io/logos-co/nomos-node:testnet",
        "volumes": ["./cl_config:/etc/nomos", "./kzgrs/kzgrs_test_params.bin:/kzgrs_test_params:z"],
        "ports": ["3000/udp", "18080/tcp"],
        "entrypoint": "/etc/nomos/scripts/run_nomos_executor.sh",
    },
    "cfgsync": {
        "image": "ghcr.io/logos-co/nomos-node:testnet",
        "volumes": ["./cl_config:/etc/nomos"],
        "ports": "",
        "entrypoint": "/etc/nomos/scripts/run_cfgsync.sh",
    },
}
