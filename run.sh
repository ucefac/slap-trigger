#!/bin/bash
#
# Convenience wrapper to run slap-trigger with proper user context
#
# Problem: IMU sensor requires root (sudo), but CGEvent needs user session
# Solution: Use launchctl asuser to switch back to user context
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER_UID=$(id -u)

if [ "$1" != "" ] && [ "${1: -3}" == ".py" ]; then
    echo "Running Python script in user context..."
    sudo launchctl asuser "$USER_UID" uv run python "$@"
else
    if [ "$(id -u)" -eq 0 ]; then
        exec launchctl asuser "$USER_UID" uv run slap-trigger "$@"
    else
        echo "Running slap-trigger in user context (GUI session)..."
        echo "This keeps CGEvent working while allowing IMU access."
        exec sudo launchctl asuser "$USER_UID" uv run slap-trigger "$@"
    fi
fi