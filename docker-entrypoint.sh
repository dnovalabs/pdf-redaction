#!/bin/sh
# Materialize file-type secrets into the container's ephemeral filesystem.
#
# `infisical run` (in scripts/deploy.sh on the server) injects secrets as env
# vars. This app reads its config as *files*, so we write them here at startup:
# nothing is baked into the image and nothing is written to the host disk — the
# files live only in the container's writable layer and vanish when it's removed.
set -eu
umask 077

if [ -n "${CONFIG_JSON:-}" ]; then
  printf '%s' "$CONFIG_JSON" > /app/config.json
fi
if [ -n "${CREDENTIALS_JSON:-}" ]; then
  printf '%s' "$CREDENTIALS_JSON" > /app/credentials.json
fi

exec "$@"
