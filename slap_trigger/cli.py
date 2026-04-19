"""
Command-line interface for slap-trigger.
"""

import argparse
import math
import signal
import subprocess
import sys
import time
from pathlib import Path

from slap_trigger.config import (
    Config,
    Action,
    DetectorSettings,
    LoggingSettings,
    load_config,
    save_config,
    get_default_config,
)
from slap_trigger.detector import DoubleTapDetector, DetectorConfig
from slap_trigger.keyboard import KeyboardSimulator
from slap_trigger.logger import (
    setup_logger,
    get_log_level,
    DEFAULT_LOG_DIR,
    log_info,
    log_error,
    log_warning,
)


def run(args: argparse.Namespace) -> None:
    """Main run function."""
    # Load configuration
    config = None
    if args.config:
        config = load_config(args.config)
    elif args.config_file.exists():
        config = load_config(args.config_file)
    else:
        config = get_default_config()
        if not args.no_init:
            save_config(config, args.config_file)
            print(f"Created default config: {args.config_file}")

    # Initialize logging
    log_dir = args.log_dir if args.log_dir else DEFAULT_LOG_DIR
    logger = setup_logger(
        log_dir=log_dir,
        max_bytes=config.logging.max_bytes,
        level=get_log_level(args.log_level or config.logging.level),
        console=args.log_console,
    )

    log_info("=== Application started ===")
    log_info(f"Log file: {log_dir / 'slap-trigger.log'}")
    log_info(
        f"Config: threshold={config.detector.threshold}g, "
        f"interval={config.detector.min_interval_ms}-{config.detector.max_interval_ms}ms"
    )

    # Show config
    print(f"Configuration:")
    print(f"  Detector threshold: {config.detector.threshold}g")
    print(
        f"  Detector interval: {config.detector.min_interval_ms}-{config.detector.max_interval_ms}ms"
    )
    print(f"  Detector cooldown: {config.detector.cooldown_ms}ms")
    print(f"  Actions: {len(config.actions)}")
    for i, action in enumerate(config.actions):
        if action.type == "keyboard":
            detail = " + ".join(action.keys) if action.keys else "(none)"
        else:  # cmd
            detail = " ".join(action.cmd) if action.cmd else "(none)"
        print(f"    {i + 1}. {action.name} [{action.type}]: {detail}")
    print()

    # Check Accessibility permission (required for CGEvent)
    try:
        from Quartz import AXIsProcessTrusted

        if not AXIsProcessTrusted():
            print(
                "Warning: Accessibility permission is required for keyboard simulation."
            )
            print(
                "Please enable in: System Settings → Privacy & Security → Accessibility"
            )
            print("Enable your terminal (Terminal/iTerm).")
            print("")
    except ImportError:
        pass  # pyobjc not available

    # Check if sensor is available
    try:
        from macimu import IMU

        if not IMU.available():
            print("Error: Accelerometer sensor not available on this device.")
            print("This feature requires Apple Silicon MacBook Pro (M2+).")
            sys.exit(1)
    except ImportError:
        print("Error: macimu not installed. Install with: pip install macimu")
        sys.exit(1)

    # Initialize detector
    detector_config = DetectorConfig(
        threshold=config.detector.threshold,
        min_interval=config.detector.min_interval_ms / 1000.0,
        max_interval=config.detector.max_interval_ms / 1000.0,
        cooldown=config.detector.cooldown_ms / 1000.0,
        debounce=config.detector.debounce_ms / 1000.0,
    )
    detector = DoubleTapDetector(detector_config)

    # Initialize keyboard simulator (CGEvent only)
    keyboard = KeyboardSimulator()

    # Get enabled actions
    actions = [a for a in config.actions if a.enabled]
    if not actions:
        print("Warning: No enabled actions in config.")
        actions = [Action(name="default", keys=["command:left", "v"])]

    # Setup signal handler for graceful shutdown
    running = True

    def signal_handler(signum, frame):
        nonlocal running
        print("\nShutting down...")
        running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Main loop
    print(f"Listening for double-tap... (Press Ctrl+C to stop)")

    # Use mock mode if requested
    if args.mock:
        _run_mock(detector, keyboard, actions, args.dry_run)
        return

    # Real sensor mode
    with IMU() as imu:
        while running:
            # Read accelerometer data
            accel = imu.latest_accel()

            if accel:
                mag = math.sqrt(accel.x**2 + accel.y**2 + accel.z**2)
                # print(
                #     f"  accel: x={accel.x:.3f} y={accel.y:.3f} z={accel.z:.3f} mag={mag:.3f}",
                #     end="\r",
                # )
                # Process through detector
                if detector.process(accel.x, accel.y, accel.z):
                    # Double tap detected!
                    print(
                        f"[{time.strftime('%H:%M:%S')}] Double tap detected!", end=" "
                    )

                    if args.dry_run:
                        print("[DRY RUN] Would trigger:", end=" ")
                        for action in actions:
                            if action.type == "cmd":
                                print(f"{action.name}: {' '.join(action.cmd)}")
                            else:
                                print(f"{action.name}: {' + '.join(action.keys)}")
                    else:
                        # Trigger actions
                        for action in actions:
                            try:
                                if action.type == "cmd":
                                    print(
                                        f"Triggering: {action.name} -> {' '.join(action.cmd)}"
                                    )
                                    subprocess.run(action.cmd, check=True)
                                else:
                                    print(f"Triggering: {action.name} -> {action.keys}")
                                    import io
                                    import sys as _sys

                                    # Capture print output from keyboard module
                                    old_stdout = _sys.stdout
                                    _sys.stdout = io.StringIO()
                                    error = None
                                    try:
                                        keyboard.press_combo(action.keys)
                                    except Exception as e:
                                        error = e
                                    finally:
                                        output = _sys.stdout.getvalue()
                                        _sys.stdout = old_stdout
                                        if output:
                                            print(output, end="")
                                        if error:
                                            print(f"  Error: {error}")
                                print(f"  Completed: {action.name}")
                            except Exception as e:
                                print(f"Error triggering action: {e}")
                        # 恢复底部实时显示
                        print("", end="\r")

            # Small sleep to prevent CPU spinning
            time.sleep(0.001)


def _run_mock(
    detector: DoubleTapDetector,
    keyboard: KeyboardSimulator,
    actions: list[Action],
    dry_run: bool,
) -> None:
    """Run in mock mode with synthetic data."""
    print("Running in MOCK mode...")
    print("Simulating accelerometer data (Ctrl+C to stop)")

    running = True

    def signal_handler(signum, frame):
        nonlocal running
        print("\nShutting down...")
        running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    start_time = time.time()
    sample_count = 0
    sample_rate = 100  # Hz

    # Simulate two taps (fast: 0.2s and 0.35s)
    tap_times = [0.2, 0.35]  # Two taps at 200ms and 350ms (150ms apart)
    next_tap_index = 0

    # Auto-exit after 1 second in mock mode
    max_duration = 1.0

    while running:
        current_time = time.time()
        elapsed = current_time - start_time

        # Generate synthetic acceleration data
        # Base: 1g at rest
        ax, ay, az = 0.0, 0.0, 1.0

        # Add tap impulse if within tap window
        if next_tap_index < len(tap_times):
            tap_time = tap_times[next_tap_index]

            if abs(elapsed - tap_time) < 0.02:
                # Impulse!
                # Alternate direction for two taps
                direction = 1 if next_tap_index == 0 else -1
                # Add some random variation
                impulse = 3.0 + (next_tap_index * 0.5)
                ax = direction * impulse * (1 + 0.1 * math.sin(elapsed * 100))
                ay = impulse * 0.5 * math.cos(elapsed * 80)
                # Check if peak
                if abs(elapsed - tap_time) < 0.005:
                    ax *= 1.5
                    ay *= 1.5
                    az = 1.0 + impulse * 0.3

                if abs(elapsed - tap_time) > 0.05:
                    next_tap_index += 1

        # Auto-exit after max_duration
        if elapsed > max_duration:
            print(f"\nMock test complete (auto-exit after {max_duration}s)")
            break

        # Process
        if detector.process(ax, ay, az):
            print(f"[{elapsed:.2f}s] Double tap detected!", end=" ")

            if dry_run:
                print("[DRY RUN] Would trigger:")
                for action in actions:
                    if action.type == "cmd":
                        print(f"  {action.name}: {' '.join(action.cmd)}")
                    else:
                        print(f"  {action.name}: {' + '.join(action.keys)}")
            else:
                for action in actions:
                    try:
                        if action.type == "cmd":
                            print(
                                f"Triggering: {action.name} -> {' '.join(action.cmd)}"
                            )
                            subprocess.run(action.cmd, check=True)
                        else:
                            print(f"Triggering: {action.name}")
                            keyboard.press_combo(action.keys)
                    except Exception as e:
                        print(f"Error: {e}")

        sample_count += 1
        time.sleep(1.0 / sample_rate)


def init_config(args: argparse.Namespace) -> None:
    """Initialize a default config file."""
    config = get_default_config()
    save_config(config, args.output)
    print(f"Created config file: {args.output}")
    print(f"\nEdit it to customize your triggers.")


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog="slap-trigger",
        description="Trigger keyboard events from MacBook accelerometer double-tap",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                      # Run with default config
  %(prog)s -c my config.json       # Run with custom config
  %(prog)s --dry-run            # Test without triggering keys
  %(prog)s --mock             # Run with simulated data
  %(prog)s init              # Create default config
        """,
    )

    parser.add_argument(
        "-c",
        "--config",
        help="Path to config file",
        metavar="FILE",
    )

    parser.add_argument(
        "--config-file",
        "-C",
        help="Config file path (default: config.json)",
        default=Path.cwd() / "config.json",
        type=Path,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Test mode without triggering real keys",
    )

    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run with simulated accelerometer data",
    )

    parser.add_argument(
        "--no-init",
        action="store_true",
        help="Don't create default config if not found",
    )

    parser.add_argument(
        "--log-level",
        choices=["debug", "info", "warning", "error"],
        help="Logging level",
    )

    parser.add_argument(
        "--log-dir",
        type=Path,
        help="Log directory (default: ~/.local/share/slap-trigger/logs/)",
    )

    parser.add_argument(
        "--log-console",
        action="store_true",
        help="Also print logs to console",
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # init command
    init_parser = subparsers.add_parser(
        "init",
        help="Create default config file",
    )
    init_parser.add_argument(
        "-o",
        "--output",
        help="Output file path (default: config.json)",
        default=Path.cwd() / "config.json",
        type=Path,
    )

    return parser


def main() -> None:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Handle commands
    if args.command == "init":
        init_config(args)
    else:
        run(args)


if __name__ == "__main__":
    main()
