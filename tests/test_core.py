"""Tests for core functionality."""

import pytest
from clip_translate.core import Config, setup_logging


class TestConfig:
    """Test configuration handling."""
    
    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = Config()
        assert config.debug is False
        assert config.log_level == "INFO"
    
    def test_custom_config(self) -> None:
        """Test custom configuration values."""
        config = Config(debug=True, log_level="DEBUG")
        assert config.debug is True
        assert config.log_level == "DEBUG"
    
    def test_invalid_extra_field(self) -> None:
        """Test that extra fields are rejected."""
        with pytest.raises(ValueError):
            Config(invalid_field="value")
