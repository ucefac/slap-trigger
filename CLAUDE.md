# Project Contract

## Project Overview

- **slap-trigger**: Trigger keyboard events from MacBook accelerometer double-tap
- **Platform**: macOS (Apple Silicon M2+ required for accelerometer sensor)
- **Language**: Python 3.10+
- **Package**: `slap_trigger`

## Build And Test

- Install: `uv sync`
- Typecheck: `python -m compileall slap_trigger/`
- Run: `./run.sh` (requires sudo for IMU access)

## Architecture Boundaries

- **slap_trigger/** - Core package
  - **detector.py** - Double tap detection algorithm (accelerometer data processing)
  - **keyboard.py** - CGEvent keyboard simulation (macOS native)
  - **config.py** - JSON configuration loading/saving
  - **cli.py** - CLI entry point and main loop

- **config.json** - User configuration file (double-tap parameters, actions)
- **pyproject.toml** - Project metadata and dependencies

## Coding Conventions

- Prefer dataclasses for configuration (detector.py, config.py)
- Use type hints for all function signatures
- Handle accessibility permissions gracefully (warn, don't crash)
- Support CGEvent keyboard backends
- Configurable delays for keyboard simulation (default 0.01s)

## Safety Rails

## NEVER

- Run without checking Accessibility permission
- Use sudo directly with CGEvent (breaks keyboard simulation)
- Commit with invalid sensor configuration for production devices

## ALWAYS

- Test with `--mock` mode before real hardware
- Verify Accessibility permission before triggering keys
- Show config before running detector
- Use `./run.sh` wrapper for production (handles sudo + user context)

## Platform Requirements

- macOS with Apple Silicon (M2+ Pro/Max) for accelerometer
- macOS 13+ for macimu library
- Accessibility permission in System Settings
- Audio playback for action type "cmd" (e.g., afplay)

## Dependencies

- **macimu** (>0.1.0) - Accelerometer access (M2+ MacBooks)
- **pyobjc** (>10.0) - macOS native APIs
- **pynput** (optional) - Alternative keyboard backend

## Known Issues

- CGEvent requires user session, IMU requires root - use `./run.sh` wrapper
- Single modifier key presses (e.g., option:right alone) may not work in some apps
- Accelerometer sensitivity varies by MacBook model