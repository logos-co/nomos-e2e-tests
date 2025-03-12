from src.env_vars import NOMOS_IMAGE, HTTP_PROXY_IMAGE

nomos_cli = {
    "reconstruct": {
        "image": NOMOS_IMAGE,
        "flags": [{"--app-blobs": [0]}],  # Value [] is a list of indexes into list of values required for the flag
        "volumes": [],
        "ports": [],
        "entrypoint": "",
    },
}

http_proxy = {
    "configurable-http-proxy": {
        "image": HTTP_PROXY_IMAGE,
        "flags": [{"--default-target": [0]}],  # Value [] is a list of indexes into list of values required for the flag
        "volumes": [],
        "ports": ["8000/tcp"],
        "entrypoint": "",
    }
}
