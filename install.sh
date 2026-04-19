#!/bin/bash
#
# Install slap-trigger as a command (runs in background, survives terminal close)
#
# This script:
# 1. Detects the project directory (where this script is located)
# 2. Generates a command script that runs nohup run.sh &
# 3. Installs to ~/.local/bin/ (or /usr/local/bin/)
# 4. Prints instructions
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_SCRIPT="$SCRIPT_DIR/run.sh"
COMMAND_NAME="slaptrigger"

INSTALL_DIR="${LOCAL_BIN:-${HOME}/.local/bin}"
COMMAND_PATH="$INSTALL_DIR/$COMMAND_NAME"

if [ ! -f "$RUN_SCRIPT" ]; then
    echo "Error: run.sh not found at $RUN_SCRIPT"
    exit 1
fi

mkdir -p "$INSTALL_DIR"

COMMAND_CONTENT=$(cat << 'CMDEOF'
#!/bin/bash
#
# slaptrigger - Start slap-trigger in background
#

SCRIPT_DIR="__RUN_SCRIPT_DIR__"
RUN_SCRIPT="$SCRIPT_DIR/run.sh"
LOG_DIR="$HOME/.local/share/slap-trigger/logs"
LOG_FILE="$LOG_DIR/slap-trigger.log"

mkdir -p "$LOG_DIR"

if [[ "$1" == "stop" ]]; then
    if pgrep -f "slap-trigger" > /dev/null 2>&1; then
        sudo pkill -f "slap-trigger" 2>/dev/null || pkill -f "slap-trigger"
        echo "slap-trigger stopped"
    else
        echo "slap-trigger is not running"
    fi
    exit 0
fi

if [[ "$1" == "status" ]]; then
    if pgrep -f "slap-trigger" > /dev/null 2>&1; then
        pid=$(pgrep -f "slap-trigger" | head -1)
        echo "slap-trigger is running (PID: $pid)"
    else
        echo "slap-trigger is not running"
    fi
    exit 0
fi

if pgrep -f "slap-trigger" > /dev/null 2>&1; then
    echo "slap-trigger is already running"
    echo "  To stop: slaptrigger stop"
    exit 0
fi

cd "$SCRIPT_DIR"
nohup "$RUN_SCRIPT" > "$LOG_FILE" 2>&1 &
echo "slap-trigger started (PID: $!)"
CMDEOF
)

echo "$COMMAND_CONTENT" | sed "s|__RUN_SCRIPT_DIR__|$SCRIPT_DIR|g" > "$COMMAND_PATH"
chmod +x "$COMMAND_PATH"

export_path_line='export PATH="$HOME/.local/bin:$PATH"'
shell_rc=""
if [ -f "$HOME/.zshrc" ]; then
    shell_rc="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    shell_rc="$HOME/.bashrc"
fi

if [ -n "$shell_rc" ] && ! grep -q "$INSTALL_DIR" "$shell_rc" 2>/dev/null; then
    echo "$export_path_line" >> "$shell_rc"
    echo "Added PATH to $shell_rc"
fi

echo "Installation complete!"
echo ""
echo "Usage:"
echo "  slaptrigger          # Start slap-trigger"
echo "  slaptrigger stop   # Stop slap-trigger (not implemented yet, use: pkill -f slap_trigger)"
echo "  tail -f ~/.local/share/slap-trigger/logs/slap-trigger.log  # View logs"
echo ""
echo "The command is installed at:"
echo "  $COMMAND_PATH"