#!/bin/bash
#
# Uninstall slap-trigger
#
# This script:
# 1. Stops running slap-trigger process
# 2. Removes the command script
# 3. Removes logs (optional)
# 4. Removes launchd plist (if exists)
#

set -e

COMMAND_PATH="$HOME/.local/bin/slaptrigger"
LOG_DIR="$HOME/.local/share/slap-trigger"

echo "Stopping slap-trigger..."
if pgrep -f "slap_trigger" > /dev/null 2>&1; then
    pkill -f "slap_trigger"
    echo "  Process stopped"
else
    echo "  Not running"
fi

echo "Removing command..."
if [ -f "$COMMAND_PATH" ]; then
    rm "$COMMAND_PATH"
    echo "  Removed $COMMAND_PATH"
else
    echo "  Command not found"
fi

echo ""
read -p "Remove logs and config? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Removing logs..."
    if [ -d "$LOG_DIR" ]; then
        rm -rf "$LOG_DIR"
        echo "  Removed $LOG_DIR"
    else
        echo "  Logs not found"
    fi
else
    echo "Keeping logs and config"
fi

echo ""
echo "Uninstall complete!"