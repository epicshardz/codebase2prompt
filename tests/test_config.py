import pytest
from pathlib import Path
from codebase2prompt.config import load_config, create_default_config

def test_create_default_config(tmp_path):
    """Test creating a default config file."""
    config_path = tmp_path / "config.ini"
    
    # Test creating new config
    create_default_config(config_path)
    assert config_path.exists()
    
    # Verify contents
    config = load_config(config_path)
    assert "include" in config["DEFAULT"]
    assert "exclude" in config["DEFAULT"]
    assert "max_file_size" in config["DEFAULT"]
    assert "clipboard" in config["DEFAULT"]
    assert "output_format" in config["DEFAULT"]

def test_load_config_with_multiple_sections(tmp_path):
    """Test loading config with multiple sections."""
    config_file = tmp_path / "test_config.ini"
    config_file.write_text("""
    [DEFAULT]
    include = *.py,*.js
    exclude = tests/*,node_modules/*
    
    [custom]
    custom_setting = value
    """)
    
    config = load_config(config_file)
    assert isinstance(config, dict)
    assert len(config) == 2
    assert "DEFAULT" in config
    assert "custom" in config
    assert config["custom"]["custom_setting"] == "value"

def test_load_invalid_config(tmp_path):
    """Test loading invalid config files."""
    # Empty config
    empty_config = tmp_path / "empty.ini"
    empty_config.touch()
    with pytest.raises(ValueError):
        load_config(empty_config)
        
    # Invalid format
    invalid_config = tmp_path / "invalid.ini"
    invalid_config.write_text("invalid content")
    with pytest.raises(ValueError):
        load_config(invalid_config)

def test_load_nonexistent_config():
    """Test loading non-existent config file."""
    with pytest.raises(ValueError):
        load_config(Path("nonexistent.ini"))
