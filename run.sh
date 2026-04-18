#!/bin/bash
#
# Convenience wrapper to run slap-trigger with proper user context
#
# Problem: IMU sensor requires root (sudo), but CGEvent needs user session
# Solution: Use launchctl asuser to switch back to user context
#

# Get current user UID
USER_UID=$(id -u)

# If a Python script is passed, run it; otherwise run slap-trigger
if [ "$1" != "" ] && [ "${1: -3}" == ".py" ]; then
    echo "Running Python script in user context..."
    sudo launchctl asuser "$USER_UID" uv run python "$@"
else
    echo "Running slap-trigger in user context (GUI session)..."
    echo "This keeps CGEvent working while allowing IMU access."
    echo ""
    # Use sudo + launchctl asuser to run in user's GUI session
    sudo launchctl asuser "$USER_UID" uv run slap-trigger "$@"
fi