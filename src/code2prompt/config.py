"""Configuration module for Codebase2Prompt."""

import configparser
from pathlib import Path
from typing import Dict, Optional
import typer

DEFAULT_CONFIG = {
    "include": "*.py,*.js,*.ts,*.html,*.css",
    "exclude": "tests/*,node_modules/*,venv/*",
    "max_file_size": "1048576",  # 1MB
    "clipboard": "true",
    "auto_copy": "true",
    "output_format": "markdown"
}

def validate_and_normalize_config(config: configparser.ConfigParser) -> Dict[str, Dict[str, str]]:
    """Validate configuration content and provide defaults for missing values.
    
    Args:
        config: ConfigParser instance to validate
        
    Returns:
        Dictionary with normalized config values
        
    Raises:
        ValueError: If config values are invalid
    """
    if not config.sections() and not config.defaults():
        raise ValueError("Empty config file")
        
    result = {"DEFAULT": DEFAULT_CONFIG.copy()}
    
    if config.defaults():
        # Validate and normalize DEFAULT section values
        defaults = dict(config.defaults())
        
        # Validate max_file_size is a number
        try:
            int(defaults.get("max_file_size", DEFAULT_CONFIG["max_file_size"]))
        except ValueError:
            defaults["max_file_size"] = DEFAULT_CONFIG["max_file_size"]
            
        # Normalize clipboard value
        clipboard = str(defaults.get("clipboard", DEFAULT_CONFIG["clipboard"])).lower()
        if clipboard not in {"true", "false"}:
            defaults["clipboard"] = DEFAULT_CONFIG["clipboard"]
            
        # Normalize output format
        output_format = str(defaults.get("output_format", DEFAULT_CONFIG["output_format"])).lower()
        if output_format not in {"markdown", "json", "yaml"}:
            defaults["output_format"] = DEFAULT_CONFIG["output_format"]
            
        result["DEFAULT"].update(defaults)
        
    # Add other sections
    for section in config.sections():
        result[section] = dict(config[section])
        
    return result

def load_config(config_path: Path) -> Dict[str, Dict[str, str]]:
    """Load and validate configuration from file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Dictionary of configuration sections with their values
        
    Raises:
        ValueError: If config file format is invalid or empty
    """
    config = configparser.ConfigParser()
    
    # Read config file
    try:
        with open(config_path) as f:
            config.read_file(f)
    except configparser.Error as e:
        raise ValueError(f"Invalid config file format: {e}")
    except Exception as e:
        raise ValueError(f"Error reading config file: {e}")
    
    # Validate and normalize config
    return validate_and_normalize_config(config)

def create_default_config(config_path: str | Path) -> None:
    """Create a default configuration file.
    
    Args:
        config_path: Path where config file should be created
        
    Raises:
        IOError: If file cannot be written
        typer.Abort: If user aborts overwrite
    """
    path = Path(str(config_path))
    if path.exists():
        if not typer.confirm(f"Config file {path} already exists. Overwrite?"):
            raise typer.Abort()
    
    config = configparser.ConfigParser()
    config["DEFAULT"] = DEFAULT_CONFIG
    
    try:
        with open(path, "w") as f:
            config.write(f)
    except Exception as e:
        raise IOError(f"Failed to create config file: {e}")
