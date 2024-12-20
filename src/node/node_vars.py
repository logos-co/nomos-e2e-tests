nomos_nodes = {
    "nomos": {
        "image": "nomos/nomos:latest",
        "volumes": ["./testnet:/etc/nomos", "./tests/kzgrs/kzgrs_test_params:/kzgrs_test_params:z"],
        "ports": ["3000/udp", "18080/tcp"],
        "entrypoint": "/etc/nomos/scripts/run_nomos_node.sh",
    },
    "nomos_executor": {
        "image": "nomos/nomos:latest",
        "volumes": ["./testnet:/etc/nomos", "./tests/kzgrs/kzgrs_test_params:/kzgrs_test_params:z"],
        "ports": ["3000/udp", "18080/tcp"],
        "entrypoint": "/etc/nomos/scripts/run_nomos_executor.sh",
    },
    "cfgsync": {"image": "nomos/nomos:latest", "volumes": ["./testnet:/etc/nomos"], "ports": "", "entrypoint": "/etc/nomos/scripts/run_cfgsync.sh"},
}
