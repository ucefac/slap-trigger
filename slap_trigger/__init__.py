"""
slap-trigger: Trigger keyboard events from MacBook accelerometer double-tap
"""

from slap_trigger.detector import DoubleTapDetector, DetectorConfig
from slap_trigger.keyboard import KeyboardSimulator
from slap_trigger.config import Config, load_config

__version__ = "0.1.0"

__all__ = [
    "DoubleTapDetector",
    "DetectorConfig",
    "KeyboardSimulator",
    "Config",
    "load_config",
]
