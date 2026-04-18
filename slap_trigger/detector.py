"""
Double-tap detector using accelerometer data.
"""

import math
import time
from dataclasses import dataclass


@dataclass
class DetectorConfig:
    """Configuration for the double-tap detector."""

    threshold: float = 2.0  # g threshold for tap detection
    min_interval: float = 0.05  # min interval between taps (seconds)
    max_interval: float = 0.5  # max interval between taps (seconds)
    cooldown: float = 0.75  # cooldown after triggered double-tap (seconds)
    debounce: float = 0.03  # debounce after first tap to ignore rapid peaks (seconds)


class DoubleTapDetector:
    """Detects double-tap gestures from accelerometer data.

    The detector monitors acceleration magnitude and identifies double-tap
    patterns based on two peaks within a configurable time window.

    Usage:
        detector = DoubleTapDetector()

        # Process each accelerometer sample
        is_double_tap = detector.process(ax, ay, az)

        if is_double_tap:
            print("Double tap detected!")
    """

    def __init__(self, config: DetectorConfig | None = None):
        self.config = config or DetectorConfig()

        self._last_accel: tuple[float, float, float] = (0.0, 0.0, 0.0)
        self._last_tap_time: float = 0
        self._first_tap_time: float = 0
        self._tap_count: int = 0
        self._last_trigger_time: float = 0
        self._in_cooldown: bool = False

    def process(self, ax: float, ay: float, az: float) -> bool:
        """Process accelerometer data and detect double-tap.

        Args:
            ax: X-axis acceleration in g
            ay: Y-axis acceleration in g
            az: Z-axis acceleration in g

        Returns:
            True if a double-tap pattern is detected
        """
        current_time = time.time()

        # Check cooldown
        if self._in_cooldown:
            if current_time - self._last_trigger_time >= self.config.cooldown:
                self._in_cooldown = False
                self._tap_count = 0
            else:
                return False

        # Calculate magnitude (accelerometer reads ~1g at rest due to gravity)
        magnitude = math.sqrt(ax * ax + ay * ay + az * az)
        self._last_accel = (ax, ay, az)

        # Detect tap (peak above threshold)
        if magnitude >= self.config.threshold:
            # Debounce: ignore rapid peaks within debounce window after first tap
            if (
                self._tap_count > 0
                and (current_time - self._last_tap_time) < self.config.debounce
            ):
                return False
            # Valid tap - calculate time since first tap for debug
            time_since_first = (
                current_time - self._first_tap_time if self._tap_count > 0 else 0
            )
            print(
                f"\n[TAP] mag={magnitude:.3f} count={self._tap_count} time={current_time:.3f} interval={time_since_first * 1000:.0f}ms"
            )
            return self._handle_tap(current_time)

        return False

    def _handle_tap(self, current_time: float) -> bool:
        """Handle a detected tap and check for double-tap pattern."""
        time_since_first_tap = current_time - self._first_tap_time

        if self._tap_count == 0:
            # First tap
            self._first_tap_time = current_time
            self._last_tap_time = current_time
            self._tap_count = 1
            return False

        elif self._tap_count == 1:
            # Second tap - check valid time window (debounce is handled in process())
            if (
                self.config.min_interval
                <= time_since_first_tap
                <= self.config.max_interval
            ):
                # Double tap detected!
                self._last_trigger_time = current_time
                self._in_cooldown = True
                self._tap_count = 0
                return True
            elif time_since_first_tap > self.config.max_interval:
                # Too long since first tap - reset and start new tap
                self._first_tap_time = current_time
                self._last_tap_time = current_time
                self._tap_count = 1
                return False
            else:
                # Too soon (but debounce passed) - ignore
                return False

        return False

    def reset(self):
        """Reset the detector state."""
        self._tap_count = 0
        self._last_tap_time = 0
        self._first_tap_time = 0
        self._last_trigger_time = 0
        self._in_cooldown = False
