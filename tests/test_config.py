# MTR DUAT - Config Module Tests
"""TDD tests for config.py - written BEFORE implementation."""

import json
import os
import pytest
from pathlib import Path

from config import DEFAULT_CONFIG, load_app_config, save_app_config, _get_config_path


class TestDefaultConfig:
    """Tests for DEFAULT_CONFIG structure."""

    @pytest.mark.unit
    def test_default_config_has_required_keys(self):
        required_keys = {"last_folder", "language", "dark_mode", "default_productivity", "keywords"}
        assert set(DEFAULT_CONFIG.keys()) == required_keys

    @pytest.mark.unit
    def test_default_config_types(self):
        assert isinstance(DEFAULT_CONFIG["last_folder"], str)
        assert isinstance(DEFAULT_CONFIG["language"], str)
        assert isinstance(DEFAULT_CONFIG["dark_mode"], bool)
        assert isinstance(DEFAULT_CONFIG["default_productivity"], (int, float))
        assert isinstance(DEFAULT_CONFIG["keywords"], list)

    @pytest.mark.unit
    def test_default_config_values(self):
        assert DEFAULT_CONFIG["last_folder"] == ""
        assert DEFAULT_CONFIG["language"] == "en"
        assert DEFAULT_CONFIG["dark_mode"] is False
        assert DEFAULT_CONFIG["default_productivity"] == 1.0
        assert DEFAULT_CONFIG["keywords"] == ["CBM", "CM", "PA work", "HLM", "Provide"]

    @pytest.mark.unit
    def test_default_config_is_not_mutated_by_load(self, tmp_config_file: Path, monkeypatch):
        """Loading config must not mutate DEFAULT_CONFIG."""
        monkeypatch.setattr("config._get_config_path", lambda: tmp_config_file)
        original = DEFAULT_CONFIG.copy()
        _ = load_app_config()
        assert DEFAULT_CONFIG == original


class TestGetConfigPath:
    """Tests for _get_config_path."""

    @pytest.mark.unit
    def test_returns_path_object(self):
        result = _get_config_path()
        assert isinstance(result, Path)

    @pytest.mark.unit
    def test_config_filename(self):
        result = _get_config_path()
        assert result.name == "mtr_duat_config.json"

    @pytest.mark.unit
    def test_env_override(self, tmp_path: Path, monkeypatch):
        """DUAT_CONFIG_PATH env var overrides default path."""
        custom_path = str(tmp_path / "custom_config.json")
        monkeypatch.setenv("DUAT_CONFIG_PATH", custom_path)
        result = _get_config_path()
        assert result == Path(custom_path)


class TestLoadAppConfig:
    """Tests for load_app_config."""

    @pytest.mark.unit
    def test_returns_defaults_when_no_file(self, tmp_config_file: Path, monkeypatch):
        """When config file does not exist, return defaults."""
        monkeypatch.setattr("config._get_config_path", lambda: tmp_config_file)
        config = load_app_config()
        assert config == DEFAULT_CONFIG

    @pytest.mark.unit
    def test_returns_dict(self, tmp_config_file: Path, monkeypatch):
        monkeypatch.setattr("config._get_config_path", lambda: tmp_config_file)
        config = load_app_config()
        assert isinstance(config, dict)

    @pytest.mark.unit
    def test_loads_saved_values(self, tmp_config_file: Path, monkeypatch):
        """Saved values are loaded correctly."""
        monkeypatch.setattr("config._get_config_path", lambda: tmp_config_file)
        saved = {"last_folder": "C:\\Data", "language": "zh", "dark_mode": True,
                 "default_productivity": 3.0, "keywords": ["CBM"]}
        tmp_config_file.write_text(json.dumps(saved), encoding="utf-8")
        config = load_app_config()
        assert config["last_folder"] == "C:\\Data"
        assert config["language"] == "zh"
        assert config["dark_mode"] is True
        assert config["default_productivity"] == 3.0
        assert config["keywords"] == ["CBM"]

    @pytest.mark.unit
    def test_merges_with_defaults_partial_file(self, tmp_config_file: Path, monkeypatch):
        """Partial config file is merged with defaults for missing keys."""
        monkeypatch.setattr("config._get_config_path", lambda: tmp_config_file)
        partial = {"language": "zh"}
        tmp_config_file.write_text(json.dumps(partial), encoding="utf-8")
        config = load_app_config()
        assert config["language"] == "zh"
        assert config["last_folder"] == DEFAULT_CONFIG["last_folder"]
        assert config["dark_mode"] == DEFAULT_CONFIG["dark_mode"]
        assert config["default_productivity"] == DEFAULT_CONFIG["default_productivity"]
        assert config["keywords"] == DEFAULT_CONFIG["keywords"]

    @pytest.mark.unit
    def test_handles_corrupted_json(self, tmp_config_file: Path, monkeypatch):
        """Corrupted JSON file returns defaults and logs warning."""
        monkeypatch.setattr("config._get_config_path", lambda: tmp_config_file)
        tmp_config_file.write_text("{invalid json!!!", encoding="utf-8")
        config = load_app_config()
        assert config == DEFAULT_CONFIG

    @pytest.mark.unit
    def test_handles_empty_file(self, tmp_config_file: Path, monkeypatch):
        """Empty file returns defaults."""
        monkeypatch.setattr("config._get_config_path", lambda: tmp_config_file)
        tmp_config_file.write_text("", encoding="utf-8")
        config = load_app_config()
        assert config == DEFAULT_CONFIG

    @pytest.mark.unit
    def test_handles_non_dict_json(self, tmp_config_file: Path, monkeypatch):
        """JSON file containing a list (not dict) returns defaults."""
        monkeypatch.setattr("config._get_config_path", lambda: tmp_config_file)
        tmp_config_file.write_text('["not", "a", "dict"]', encoding="utf-8")
        config = load_app_config()
        assert config == DEFAULT_CONFIG

    @pytest.mark.unit
    def test_handles_read_os_error(self, tmp_path: Path, monkeypatch):
        """OSError during file read returns defaults."""
        fake_path = tmp_path / "config.json"
        fake_path.write_text("{}", encoding="utf-8")
        monkeypatch.setattr("config._get_config_path", lambda: fake_path)

        def raise_os_error(*args, **kwargs):
            raise OSError("Permission denied")

        monkeypatch.setattr(Path, "read_text", raise_os_error)
        config = load_app_config()
        assert config == DEFAULT_CONFIG

    @pytest.mark.unit
    def test_ignores_unknown_keys(self, tmp_config_file: Path, monkeypatch):
        """Unknown keys in config file are preserved (forward compat)."""
        monkeypatch.setattr("config._get_config_path", lambda: tmp_config_file)
        saved = {**DEFAULT_CONFIG, "future_setting": True}
        tmp_config_file.write_text(json.dumps(saved), encoding="utf-8")
        config = load_app_config()
        assert config["future_setting"] is True

    @pytest.mark.unit
    def test_returns_new_dict_each_call(self, tmp_config_file: Path, monkeypatch):
        """Each call returns a fresh dict (no shared mutable state)."""
        monkeypatch.setattr("config._get_config_path", lambda: tmp_config_file)
        config1 = load_app_config()
        config2 = load_app_config()
        assert config1 is not config2


class TestSaveAppConfig:
    """Tests for save_app_config."""

    @pytest.mark.unit
    def test_returns_true_on_success(self, tmp_config_file: Path, monkeypatch):
        monkeypatch.setattr("config._get_config_path", lambda: tmp_config_file)
        result = save_app_config(DEFAULT_CONFIG.copy())
        assert result is True

    @pytest.mark.unit
    def test_creates_file(self, tmp_config_file: Path, monkeypatch):
        """Config file is created if it does not exist."""
        monkeypatch.setattr("config._get_config_path", lambda: tmp_config_file)
        assert not tmp_config_file.exists()
        save_app_config(DEFAULT_CONFIG.copy())
        assert tmp_config_file.exists()

    @pytest.mark.unit
    def test_saved_file_is_valid_json(self, tmp_config_file: Path, monkeypatch):
        monkeypatch.setattr("config._get_config_path", lambda: tmp_config_file)
        save_app_config(DEFAULT_CONFIG.copy())
        content = json.loads(tmp_config_file.read_text(encoding="utf-8"))
        assert isinstance(content, dict)

    @pytest.mark.unit
    def test_saved_values_match(self, tmp_config_file: Path, monkeypatch, sample_config: dict):
        monkeypatch.setattr("config._get_config_path", lambda: tmp_config_file)
        save_app_config(sample_config)
        loaded = json.loads(tmp_config_file.read_text(encoding="utf-8"))
        assert loaded == sample_config

    @pytest.mark.unit
    def test_overwrites_existing_file(self, tmp_config_file: Path, monkeypatch):
        monkeypatch.setattr("config._get_config_path", lambda: tmp_config_file)
        save_app_config({**DEFAULT_CONFIG, "language": "en"})
        save_app_config({**DEFAULT_CONFIG, "language": "zh"})
        loaded = json.loads(tmp_config_file.read_text(encoding="utf-8"))
        assert loaded["language"] == "zh"

    @pytest.mark.unit
    def test_returns_false_on_write_failure(self, tmp_path: Path, monkeypatch):
        """Returns False when file cannot be written (e.g., invalid path)."""
        bad_path = tmp_path / "nonexistent_dir" / "sub" / "config.json"
        monkeypatch.setattr("config._get_config_path", lambda: bad_path)
        result = save_app_config(DEFAULT_CONFIG.copy())
        assert result is False

    @pytest.mark.unit
    def test_roundtrip(self, tmp_config_file: Path, monkeypatch, sample_config: dict):
        """Save then load returns the same config."""
        monkeypatch.setattr("config._get_config_path", lambda: tmp_config_file)
        save_app_config(sample_config)
        loaded = load_app_config()
        assert loaded == sample_config

    @pytest.mark.unit
    def test_file_encoding_utf8(self, tmp_config_file: Path, monkeypatch):
        """Config file is saved with UTF-8 encoding (supports Chinese paths)."""
        monkeypatch.setattr("config._get_config_path", lambda: tmp_config_file)
        config = {**DEFAULT_CONFIG, "last_folder": "C:\\報告\\每日"}
        save_app_config(config)
        content = tmp_config_file.read_text(encoding="utf-8")
        assert "每日" in content
