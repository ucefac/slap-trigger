"""
Keyboard simulator using macOS CGEvent (ctypes).
Supports left/right modifier key distinction.
"""

import ctypes
import time
from ctypes import util, CDLL

from slap_trigger.logger import log_debug

# Load CoreGraphics directly via ctypes (same as trigger_hotkey.py)
_core_graphics = CDLL(util.find_library("CoreGraphics"))

kCGHIDEventTap = 0x0
kCGEventFlagMaskCommand = 0x00010000
kCGEventFlagMaskShift = 0x00020000
kCGEventFlagMaskControl = 0x00040000
kCGEventFlagMaskAlternate = 0x00080000

# Bind functions
CGEventCreateKeyboardEvent = _core_graphics.CGEventCreateKeyboardEvent
CGEventCreateKeyboardEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_bool]
CGEventCreateKeyboardEvent.restype = ctypes.c_void_p

CGEventSetFlags = _core_graphics.CGEventSetFlags
CGEventSetFlags.argtypes = [ctypes.c_void_p, ctypes.c_uint64]

CGEventPost = _core_graphics.CGEventPost
CGEventPost.argtypes = [ctypes.c_int, ctypes.c_void_p]


# Virtual key codes for special keys
# Reference: https://github.com/randomecho/mac-keycodes
KEY_CODES = {
    # Letters
    "a": 0x00,
    "b": 0x0B,
    "c": 0x08,
    "d": 0x02,
    "e": 0x0E,
    "f": 0x03,
    "g": 0x05,
    "h": 0x04,
    "i": 0x22,
    "j": 0x26,
    "k": 0x28,
    "l": 0x25,
    "m": 0x2E,
    "n": 0x2D,
    "o": 0x1F,
    "p": 0x23,
    "q": 0x0C,
    "r": 0x15,
    "s": 0x01,
    "t": 0x17,
    "u": 0x20,
    "v": 0x09,
    "w": 0x0D,
    "x": 0x07,
    "y": 0x10,
    "z": 0x06,
    # Numbers
    "0": 0x1D,
    "1": 0x12,
    "2": 0x13,
    "3": 0x14,
    "4": 0x15,
    "5": 0x17,
    "6": 0x16,
    "7": 0x0F,
    "8": 0x20,
    "9": 0x24,
    # Punctuation
    ".": 0x41,
    "period": 0x41,
    ",": 0x2B,
    "comma": 0x2B,
    ";": 0x29,
    "semicolon": 0x29,
    "'": 0x27,
    "quote": 0x27,
    "[": 0x21,
    "]": 0x1E,
    "/": 0x2C,
    "slash": 0x2C,
    "\\": 0x2A,
    "backslash": 0x2A,
    "-": 0x1B,
    "dash": 0x1B,
    "=": 0x18,
    "equals": 0x18,
    # Special keys
    "return": 0x24,
    "enter": 0x24,
    "tab": 0x30,
    "space": 0x31,
    "delete": 0x33,
    "backspace": 0x33,
    "escape": 0x35,
    "esc": 0x35,
    "capslock": 0x39,
    # Function keys
    "f1": 0x7A,
    "f2": 0x78,
    "f3": 0x63,
    "f4": 0x76,
    "f5": 0x60,
    "f6": 0x61,
    "f7": 0x62,
    "f8": 0x64,
    "f9": 0x65,
    "f10": 0x6D,
    "f11": 0x67,
    "f12": 0x6F,
    # Arrow keys
    "left": 0x7B,
    "right": 0x7C,
    "down": 0x7D,
    "up": 0x7E,
    # Navigation keys
    "home": 0x73,
    "end": 0x77,
    "pageup": 0x74,
    "pagedown": 0x79,
    # Modifier keys (single - can be left or right)
    "command": 0x37,
    "control": 0x3B,
    "option": 0x3A,
    "alt": 0x3A,
    "shift": 0x38,
    # Left modifier keys
    "command:left": 0x37,  # Left Command (0x37)
    "control:left": 0x3B,  # Left Control (0x3B)
    "option:left": 0x3A,  # Left Option (0x3A)
    "shift:left": 0x38,  # Left Shift (0x38)
    # Right modifier keys
    "command:right": 0x36,  # Right Command (0x36)
    "control:right": 0x3E,  # Right Control (0x3E)
    "option:right": 0x3D,  # Right Option (0x3D)
    "shift:right": 0x3C,  # Right Shift (0x3C)
}

# Modifier flag mappings
MODIFIER_FLAGS = {
    "command:left": kCGEventFlagMaskCommand,
    "command:right": kCGEventFlagMaskCommand,
    "command": kCGEventFlagMaskCommand,
    "control:left": kCGEventFlagMaskControl,
    "control:right": kCGEventFlagMaskControl,
    "control": kCGEventFlagMaskControl,
    "option:left": kCGEventFlagMaskAlternate,
    "option:right": kCGEventFlagMaskAlternate,
    "option": kCGEventFlagMaskAlternate,
    "alt": kCGEventFlagMaskAlternate,
    "shift:left": kCGEventFlagMaskShift,
    "shift:right": kCGEventFlagMaskShift,
    "shift": kCGEventFlagMaskShift,
}


class KeyboardSimulator:
    """Simulate keyboard events on macOS.

    Supports single key presses and modifier combinations.
    Distinguishes between left and right modifier keys.

    Usage:
        kb = KeyboardSimulator()

        # Single key
        kb.press_key('space')

        # Combination key (e.g., Cmd+V)
        kb.press_combo(['command:left', 'v'])

        # Multiple keys
        kb.press_combo(['command:left', 'shift', '4'])
    """

    def __init__(self, delay: float = 0.01):
        """Initialize keyboard simulator.

        Args:
            delay: Delay between key press and release (seconds)
        """
        self._delay = delay
        log_debug(f"KeyboardSim initialized with delay={delay}")

    def press_key(self, key: str) -> None:
        """Press and release a single key.

        Args:
            key: Key name (e.g., 'a', 'space', 'return')
        """
        key_lower = key.lower()

        if key_lower not in KEY_CODES:
            raise ValueError(f"Unknown key: {key}")
        key_code = KEY_CODES[key_lower]

        # Key down (no flags - same as trigger_hotkey.py)
        event = CGEventCreateKeyboardEvent(None, key_code, True)
        CGEventPost(kCGHIDEventTap, event)
        time.sleep(self._delay)

        # Key up
        event = CGEventCreateKeyboardEvent(None, key_code, False)
        CGEventPost(kCGHIDEventTap, event)
        time.sleep(self._delay)

    def press_combo(self, keys: list[str]) -> None:
        """Press a combination of keys.

        The last key in the list is the main key, others are modifiers.
        Supports left/right modifier distinction.

        Args:
            keys: List of keys (e.g., ['command:left', 'v'])

        Example:
            kb.press_combo(['command:left', 'v'])      # Cmd+V
            kb.press_combo(['command:left', '5'])     # Cmd+5
            kb.press_combo(['command:left', 'shift', '4'])  # Cmd+Shift+4
        """
        if not keys:
            raise ValueError("At least one key is required")

        if len(keys) == 1:
            self.press_key(keys[0])
            return

        # Use CGEvent directly
        # Separate modifiers and main key
        modifiers = []
        main_key = None

        for key in keys:
            key_lower = key.lower()
            if key_lower in MODIFIER_FLAGS:
                modifiers.append(key_lower)
            else:
                main_key = key_lower

        if main_key is None:
            # All keys are modifiers - press the last one as main key
            main_key = modifiers.pop()

        # Get main key code
        if main_key not in KEY_CODES:
            raise ValueError(f"Unknown key: {main_key}")

        main_key_code = KEY_CODES[main_key]

        # Build modifier flags
        modifier_flags = 0
        for mod in modifiers:
            if mod in MODIFIER_FLAGS:
                modifier_flags |= MODIFIER_FLAGS[mod]

        # Press modifiers first (for modifier keys that need to be held)
        for mod in modifiers:
            self._press_modifier(mod, True)

        # Small delay for modifiers to register
        time.sleep(0.01)

        # Main key down with modifiers - use flags, not pressed modifier keys
        self._key_down_with_flags(main_key_code, modifier_flags)
        time.sleep(self._delay)

        # Main key up
        self._key_up(main_key_code)

        # Release modifiers
        time.sleep(0.001)
        for mod in reversed(modifiers):
            self._press_modifier(mod, False)

    def _key_down(self, key_code: int) -> None:
        """Press a key down."""
        event = CGEventCreateKeyboardEvent(None, key_code, True)
        CGEventPost(kCGHIDEventTap, event)
        time.sleep(self._delay)

    def _key_up(self, key_code: int) -> None:
        """Release a key."""
        event = CGEventCreateKeyboardEvent(None, key_code, False)
        CGEventPost(kCGHIDEventTap, event)
        time.sleep(self._delay)

    def _key_down_with_flags(self, key_code: int, flags: int) -> None:
        """Press a key down with modifier flags."""
        event = CGEventCreateKeyboardEvent(None, key_code, True)
        if flags:
            CGEventSetFlags(event, flags)
        CGEventPost(kCGHIDEventTap, event)
        time.sleep(self._delay)

    def _press_modifier(self, modifier: str, pressed: bool) -> None:
        """Press or release a modifier key.

        Args:
            modifier: Modifier name (e.g., 'command:left')
            pressed: True for press, False for release
        """
        key_lower = modifier.lower()

        # Get key code
        if key_lower not in KEY_CODES:
            return

        key_code = KEY_CODES[key_lower]

        # Get modifier flags
        flags = MODIFIER_FLAGS.get(key_lower, 0)

        # Create event
        event = CGEventCreateKeyboardEvent(None, key_code, pressed)
        if flags:
            CGEventSetFlags(event, flags)
        CGEventPost(kCGHIDEventTap, event)
        time.sleep(self._delay)


def parse_key(key: str) -> str:
    """Parse and normalize a key string.

    Args:
        key: Key string to parse

    Returns:
        Normalized key string
    """
    return key.lower().strip()


def is_modifier(key: str) -> bool:
    """Check if a key is a modifier key.

    Args:
        key: Key string to check

    Returns:
        True if the key is a modifier
    """
    return key.lower() in MODIFIER_FLAGS


# Convenience functions
def press(key: str) -> None:
    """Press a single key."""
    kb = KeyboardSimulator()
    kb.press_key(key)


def combo(keys: list[str]) -> None:
    """Press a combination of keys."""
    kb = KeyboardSimulator()
    kb.press_combo(keys)
