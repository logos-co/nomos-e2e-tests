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


def make_mod_da_var(node_type, version, is_image=False):
    base = "nomos_executor_mod_da" if node_type == "executor" else "nomos_mod_da"
    value = f"{base}_{version}"

    if is_image:
        return value.replace("_", "-") + ":testnet"
    else:
        return value


# Configuration constants. Need to be upercase to appear in reports
DEFAULT_NOMOS_IMAGE = "ghcr.io/logos-co/nomos:testnet"
NOMOS_IMAGE = get_env_var("NOMOS_IMAGE", DEFAULT_NOMOS_IMAGE)

NOMOS_MOD_DA_IMAGE_d8bbc46 = make_mod_da_var("validator", "d8bbc46", True)
NOMOS_EXECUTOR_MOD_DA_IMAGE_d19a1f3 = make_mod_da_var("executor", "d19a1f3", True)
NOMOS_EXECUTOR_MOD_DA_IMAGE_7f54114 = make_mod_da_var("executor", "7f54114", True)
NOMOS_EXECUTOR_MOD_DA_IMAGE_4a58376 = make_mod_da_var("executor", "4a58376", True)

DEFAULT_PROXY_IMAGE = "bitnami/configurable-http-proxy:latest"
HTTP_PROXY_IMAGE = get_env_var("HTTP_PROXY_IMAGE", DEFAULT_PROXY_IMAGE)

NOMOS_CUSTOM = "nomos_custom"
NOMOS = "nomos"
NOMOS_EXECUTOR = "nomos_executor"
CFGSYNC = "cfgsync"

NOMOS_EXECUTOR_MOD_DA_d19a1f3 = make_mod_da_var("executor", "d19a1f3")
NOMOS_EXECUTOR_MOD_DA_7f54114 = make_mod_da_var("executor", "7f54114")
NOMOS_EXECUTOR_MOD_DA_4a58376 = make_mod_da_var("executor", "4a58376")

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
