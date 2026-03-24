#!/bin/bash
# Media Optimization Wrapper Script

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

python3 "$SCRIPT_DIR/scripts/optimize_media.py" "$@"
