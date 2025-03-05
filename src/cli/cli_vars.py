from src.env_vars import NOMOS_IMAGE

nomos_cli = {
    "reconstruct": {
        "image": NOMOS_IMAGE,
        "flags": [{"--app-blobs": [0]}],  # Value [] is a list of indexes into list of values required for the flag
        "volumes": [],
        "ports": [],
        "entrypoint": "",
    },
    "client_node": {
        "image": NOMOS_IMAGE,
        "flags": [],
        "volumes": [],
        "ports": [],
        "entrypoint": "",
    },
}
