"""Tests for cross-platform storage behavior."""

from fp.utils.storage import GlobalConfig, StorageManager


def test_config_roundtrip(tmp_path) -> None:
    """Save and load config on every supported operating system."""
    storage = StorageManager(tmp_path)
    config = GlobalConfig(default_host="host-1")

    storage.save_config(config)

    assert storage.load_config() == config
