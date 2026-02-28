#!/bin/bash
# Media Optimization Wrapper Script
# Automatically sets up PATH for FFmpeg and runs the optimization

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Add .bin to PATH (where FFmpeg binaries are)
export PATH="$SCRIPT_DIR/.bin:$PATH"

# Run the optimization script with all passed arguments
python3 "$SCRIPT_DIR/execution/optimize_media.py" "$@"
