#!/bin/sh

set -e

poe_api run -H "${HOST}" -p "${PORT}" -v "${INSTANCE}"