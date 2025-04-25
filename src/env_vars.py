import os

from dotenv import load_dotenv

load_dotenv()  # This will load environment variables from a .env file if it exists


def get_env_var(var_name, default=None):
    env_var = os.getenv(var_name, default)
    if env_var in [None, ""]:
        print(f"{var_name} is not set; using default value: {default}")
        env_var = default
    print(f"{var_name}: {env_var}")
    return env_var


# Configuration constants. Need to be upercase to appear in reports
DEFAULT_NOMOS_IMAGE = "ghcr.io/logos-co/nomos:testnet"
NOMOS_IMAGE = get_env_var("NOMOS_IMAGE", DEFAULT_NOMOS_IMAGE)

DEFAULT_PROXY_IMAGE = "bitnami/configurable-http-proxy:latest"
HTTP_PROXY_IMAGE = get_env_var("HTTP_PROXY_IMAGE", DEFAULT_PROXY_IMAGE)

NOMOS = "nomos"
NOMOS_EXECUTOR = "nomos_executor"
CFGSYNC = "cfgsync"

NODE_1 = get_env_var("NODE_1", NOMOS)
NODE_2 = get_env_var("NODE_2", NOMOS_EXECUTOR)
NODE_3 = get_env_var("NODE_3", CFGSYNC)

NOMOS_CLI = "/usr/bin/nomos-cli"

ADDITIONAL_NODES = get_env_var("ADDITIONAL_NODES", f"{NOMOS},{NOMOS}")
# more nodes need to follow the NODE_X pattern
DOCKER_LOG_DIR = get_env_var("DOCKER_LOG_DIR", "./log/docker")
NETWORK_NAME = get_env_var("NETWORK_NAME", "nomos")
SUBNET = get_env_var("SUBNET", "172.19.0.0/16")
IP_RANGE = get_env_var("IP_RANGE", "172.19.0.0/24")
GATEWAY = get_env_var("GATEWAY", "172.19.0.1")
RUNNING_IN_CI = get_env_var("CI")
API_REQUEST_TIMEOUT = get_env_var("API_REQUEST_TIMEOUT", 20)
CHECK_LOG_ERRORS = get_env_var("CHECK_LOG_ERRORS", False)
CONSENSUS_SLOT_TIME = get_env_var("CONSENSUS_SLOT_TIME", 5)
