"""
Configuration loading from JSON files.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DetectorSettings:
    """Detector configuration."""

    threshold: float = 2.0
    min_interval_ms: int = 50
    max_interval_ms: int = 500
    cooldown_ms: int = 750
    debounce_ms: int = 30

    def to_dict(self) -> dict:
        return {
            "threshold": self.threshold,
            "min_interval_ms": self.min_interval_ms,
            "max_interval_ms": self.max_interval_ms,
            "cooldown_ms": self.cooldown_ms,
            "debounce_ms": self.debounce_ms,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DetectorSettings":
        return cls(
            threshold=data.get("threshold", 2.0),
            min_interval_ms=data.get("min_interval_ms", 50),
            max_interval_ms=data.get("max_interval_ms", 500),
            cooldown_ms=data.get("cooldown_ms", 750),
            debounce_ms=data.get("debounce_ms", 30),
        )

    def to_seconds(self) -> dict:
        """Convert to seconds for detector."""
        return {
            "threshold": self.threshold,
            "min_interval": self.min_interval_ms / 1000.0,
            "max_interval": self.max_interval_ms / 1000.0,
            "cooldown": self.cooldown_ms / 1000.0,
            "debounce": self.debounce_ms / 1000.0,
        }


@dataclass
class Action:
    """A trigger action.

    Attributes:
        name: Action name
        type: Action type - "keyboard" or "cmd"
        keys: Key combination for keyboard type (e.g., ["command:left", "v"])
        cmd: Command list for cmd type (e.g., ["open", "/Applications/Safari.app"])
        enabled: Whether the action is enabled
    """

    name: str
    type: str = "keyboard"  # "keyboard" or "cmd"
    keys: list[str] = field(default_factory=list)
    cmd: list[str] = field(default_factory=list)
    enabled: bool = True

    def to_dict(self) -> dict:
        result = {
            "name": self.name,
            "type": self.type,
            "enabled": self.enabled,
        }
        if self.type == "keyboard":
            result["keys"] = self.keys
        else:  # cmd
            result["cmd"] = self.cmd
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "Action":
        action_type = data.get("type", "keyboard")
        return cls(
            name=data.get("name", "default"),
            type=action_type,
            keys=data.get("keys", []),
            cmd=data.get("cmd", []),
            enabled=data.get("enabled", True),
        )


@dataclass
class Config:
    """Main configuration."""

    detector: DetectorSettings = field(default_factory=DetectorSettings)
    actions: list[Action] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        detector_data = data.get("detector", {})
        actions_data = data.get("actions", [])

        return cls(
            detector=DetectorSettings.from_dict(detector_data),
            actions=[Action.from_dict(a) for a in actions_data],
        )

    def to_dict(self) -> dict:
        return {
            "detector": self.detector.to_dict(),
            "actions": [a.to_dict() for a in self.actions],
        }


def load_config(path: str | Path) -> Config:
    """Load configuration from a JSON file.

    Args:
        path: Path to the config file

    Returns:
        Config object

    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file is not valid JSON
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return Config.from_dict(data)


def save_config(config: Config, path: str | Path) -> None:
    """Save configuration to a JSON file.

    Args:
        config: Config object
        path: Path to save to
    """
    path = Path(path)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)


def get_default_config() -> Config:
    """Get default configuration."""
    return Config(
        detector=DetectorSettings(),
        actions=[
            Action(
                name="paste", type="keyboard", keys=["command:left", "v"], enabled=True
            ),
        ],
    )


def get_default_config_path() -> Path:
    """Get default config file path (config.json in current directory)."""
    return Path.cwd() / "config.json"


def ensure_config_exists(path: str | Path | None = None) -> Config:
    """Ensure config file exists, create default if not.

    Args:
        path: Config file path. If None, uses default path.

    Returns:
        Config object
    """
    path = Path(path) if path else get_default_config_path()

    if not path.exists():
        config = get_default_config()
        save_config(config, path)
        print(f"Created default config: {path}")
        return config

    return load_config(path)
