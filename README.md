# slap-trigger

Trigger keyboard events from MacBook Pro accelerometer double-tap gesture.

## Inspiration

This project is inspired by [apple-silicon-accelerometer](https://github.com/olvvier/apple-silicon-accelerometer).

## Overview

slap-trigger detects double-tap gestures using the built-in accelerometer on Apple Silicon MacBook Pro (M2+) and triggers keyboard shortcuts or shell commands. It's perfect for executing actions like paste, copy, or any custom key combination by simply double-tapping your MacBook.

## Requirements

- **MacBook Pro with Apple Silicon (M2+)** - Required for accelerometer sensor
- **macOS 13+** - Required for macimu library
- **Accessibility Permission** - Required for keyboard simulation

## Installation

### 1. Install the package

```bash
# Using uv (recommended)
uv sync
```

### 2. Grant Accessibility Permission

1. Go to **System Settings → Privacy & Security → Accessibility**
2. Enable your terminal app (Terminal, iTerm2, etc.)
3. The program will warn you if permission is not granted

## Usage

### Quick Start

```bash
# Run with sudo (required for IMU access)
./run.sh
```

### Configuration

Edit `config.json` to customize your triggers:

```json
{
  "detector": {
    "threshold": 1.02,
    "min_interval_ms": 180,
    "max_interval_ms": 220,
    "cooldown_ms": 1500,
    "debounce_ms": 60
  },
  "actions": [
    {
      "name": "paste",
      "type": "keyboard",
      "keys": ["command:left", "v"],
      "enabled": true
    }
  ]
}
```

### Detector Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| `threshold` | Acceleration threshold in g (1g = rest) | 2.0 |
| `min_interval_ms` | Minimum interval between taps (ms) | 50 |
| `max_interval_ms` | Maximum interval between taps (ms) | 500 |
| `cooldown_ms` | Cooldown after triggered double-tap (ms) | 750 |
| `debounce_ms` | Debounce window to ignore rapid peaks (ms) | 30 |

### Action Types

#### Keyboard Action

Trigger a keyboard shortcut:

```json
{
  "name": "my-action",
  "type": "keyboard",
  "keys": ["command:left", "c"],
  "enabled": true
}
```

Supported key formats:
- Letters: `a`, `b`, `c`, ...
- Numbers: `0`, `1`, `2`, ...
- Modifiers: `command:left`, `command:right`, `option:left`, `control`, `shift`, ...
- Special: `space`, `return`, `tab`, `delete`, `escape`, `f1`-`f12`, `left`, `right`, `up`, `down`

#### Command Action

Execute a shell command:

```json
{
  "name": "play sound",
  "type": "cmd",
  "cmd": ["afplay", "/path/to/sound.mp3"],
  "enabled": true
}
```

## Troubleshooting

### "Accelerometer sensor not available"

This feature requires Apple Silicon MacBook Pro (M2+). Older Macs don't have the required accelerometer.

### "Accessibility permission is required"

1. Open **System Settings → Privacy & Security → Accessibility**
2. Enable your terminal app

### Keys not triggering

- Some apps don't respond to single modifier key presses (e.g., `option:right`)
- Try using combination keys like `command:left` + `v`

### CGEvent not working with sudo

Use `./run.sh` wrapper instead of running directly with sudo. The wrapper uses `launchctl asuser` to switch back to your user context for keyboard simulation.

## Development

### Commands

```bash
# Install dependencies
uv sync


# Run
./run.sh
```

### Architecture

```
slap_trigger/
├── cli.py        # CLI entry point
├── config.py     # Configuration loading
├── detector.py  # Double-tap detection algorithm
└── keyboard.py # CGEvent keyboard simulation
```

## License

MIT