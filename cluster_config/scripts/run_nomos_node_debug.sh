#!/bin/sh

set -e

export CFG_FILE_PATH="/config.yaml" \
       CFG_SERVER_ADDR="http://cfgsync:4400" \
       CFG_HOST_IP=$(hostname -i) \
       CFG_HOST_IDENTIFIER="validator-$(hostname -i)" \
       LOG_LEVEL="DEBUG" \
       RISC0_DEV_MODE=true

/usr/bin/cfgsync-client && \
    exec /usr/bin/nomos-node /config.yaml
