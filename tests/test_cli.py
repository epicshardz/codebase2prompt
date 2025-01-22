import pytest
from typer.testing import CliRunner
from Codebase2Prompt.cli import cli as c2p

runner = CliRunner()

def test_cli_help():
    result = runner.invoke(c2p, ['--help'])
    assert result.exit_code == 0
    assert "Show this message and exit." in result.output

def test_cli_version():
    result = runner.invoke(c2p, ['--version'])
    assert result.exit_code == 0
    assert "version" in result.output.lower()

def test_cli_with_config():
    result = runner.invoke(c2p, ['--config', 'config.ini'])
    assert result.exit_code == 0
    # Add more assertions based on expected output

def test_create_config_overwrite(tmp_path):
    """Test --create_config with existing file."""
    config_path = tmp_path / "config.ini"
    config_path.touch()
    
    # Test abort on no confirmation
    result = runner.invoke(c2p, ['--create-config', '--config', str(config_path)], input='n\n')
    assert result.exit_code == 1
    assert "aborted" in result.output.lower()
    
    # Test successful overwrite
    result = runner.invoke(c2p, ['--create-config', '--config', str(config_path)], input='y\n')
    assert result.exit_code == 0
    assert "created new config file" in result.output.lower()

def test_config_merging(tmp_path):
    """Test config merging with CLI overrides."""
    config_path = tmp_path / "config.ini"
    config_path.write_text("""
[DEFAULT]
include = *.py
exclude = tests/*
max_file_size = 1048576
clipboard = true
output_format = markdown
""")
    
    # Test CLI override of config values
    result = runner.invoke(c2p, [
        '--config', str(config_path),
        '--exclude', 'node_modules',
        '--no-clipboard',
        '--output-format', 'json'
    ])
    assert result.exit_code == 0
    assert "json" in result.output.lower()

def test_output_formats(tmp_path):
    """Test different output formats."""
    config_path = tmp_path / "config.ini"
    config_path.write_text("""
    [DEFAULT]
    include = *.py
    exclude = tests/*
    """)
    
    # Test markdown output
    result = runner.invoke(c2p, ['--config', str(config_path)])
    assert result.exit_code == 0
    assert "# Codebase" in result.output
    
    # Test json output
    result = runner.invoke(c2p, ['--config', str(config_path), '--output-format', 'json'])
    assert result.exit_code == 0
    assert '"files":' in result.output
    
    # Test yaml output
    result = runner.invoke(c2p, ['--config', str(config_path), '--output-format', 'yaml'])
    assert result.exit_code == 0
    assert "files:" in result.output
