# MTR DUAT - Configuration Module
"""
Application configuration management.
Loads and saves JSON config file, merging saved values with defaults.

Config file location strategy (portable):
- DUAT_CONFIG_PATH env var overrides all
- Production: same directory as the executable
- Development: current working directory
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)

CONFIG_FILENAME = "mtr_duat_config.json"

DEFAULT_CONFIG: Dict = {
    "last_folder": "",
    "language": "en",
    "dark_mode": False,
    "default_productivity": 1.0,
    "keywords": ["CBM", "CM", "PA work", "HLM", "Provide"],
}


def _get_config_path() -> Path:
    """Determine the config file path based on environment."""
    env_path = os.environ.get("DUAT_CONFIG_PATH")
    if env_path:
        return Path(env_path)

    exe_dir = Path(sys.executable).parent
    exe_config = exe_dir / CONFIG_FILENAME
    if exe_dir.exists() and exe_dir != Path(sys.prefix):
        return exe_config

    return Path.cwd() / CONFIG_FILENAME


def load_app_config() -> Dict:
    """Load configuration from JSON file, merging with defaults."""
    config = {**DEFAULT_CONFIG, "keywords": list(DEFAULT_CONFIG["keywords"])}

    config_path = _get_config_path()
    if not config_path.exists():
        return config

    try:
        text = config_path.read_text(encoding="utf-8")
        if not text.strip():
            logger.warning("Config file is empty, using defaults")
            return config

        saved = json.loads(text)
        if not isinstance(saved, dict):
            logger.warning("Config file does not contain a dict, using defaults")
            return config

        config.update(saved)
        return config

    except (json.JSONDecodeError, ValueError) as e:
        logger.warning("Corrupted config file, using defaults: %s", e)
        return config
    except OSError as e:
        logger.warning("Cannot read config file, using defaults: %s", e)
        return config


def save_app_config(config: Dict) -> bool:
    """Save configuration to JSON file. Returns True on success."""
    config_path = _get_config_path()
    try:
        config_path.write_text(
            json.dumps(config, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return True
    except OSError as e:
        logger.error("Failed to save config: %s", e)
        return False
