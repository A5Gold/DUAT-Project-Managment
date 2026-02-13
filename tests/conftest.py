# MTR DUAT - Test Configuration
"""Shared fixtures for all tests."""

import pytest
import json
import tempfile
from pathlib import Path


@pytest.fixture
def tmp_config_dir(tmp_path: Path) -> Path:
    """Provide a temporary directory for config file operations."""
    return tmp_path


@pytest.fixture
def tmp_config_file(tmp_path: Path) -> Path:
    """Provide a temporary config file path (does not create the file)."""
    return tmp_path / "mtr_duat_config.json"


@pytest.fixture
def sample_config() -> dict:
    """Provide a sample configuration dict."""
    return {
        "last_folder": "C:\\Reports\\Daily",
        "language": "zh",
        "dark_mode": True,
        "default_productivity": 2.5,
        "keywords": ["CBM", "CM", "PA work", "HLM", "Provide"],
    }
