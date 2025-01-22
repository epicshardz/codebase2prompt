import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from Codebase2Prompt.cli import cli as c2p

runner = CliRunner()

def test_clipboard_copy():
    """Test clipboard copy functionality."""
    with patch('pyperclip.copy') as mock_copy, \
         patch('Codebase2Prompt.cli.get_codebase_files') as mock_files, \
         patch('Codebase2Prompt.cli.Formatter') as mock_formatter:
        mock_files.return_value = {}
        mock_formatter.return_value.format.return_value = "test output"
        # Test with clipboard disabled
        result = runner.invoke(c2p, ['.', '--no-clipboard'])
        assert result.exit_code == 0
        mock_copy.assert_not_called()
        
        # Test with clipboard enabled
        result = runner.invoke(c2p, ['.'])
        assert result.exit_code == 0
        mock_copy.assert_called_once()
        assert "copied to clipboard" in result.output

def test_clipboard_error():
    """Test clipboard error handling."""
    with patch('pyperclip.copy', side_effect=Exception("Clipboard error")), \
         patch('Codebase2Prompt.cli.get_codebase_files') as mock_files, \
         patch('Codebase2Prompt.cli.Formatter') as mock_formatter:
        mock_files.return_value = {}
        mock_formatter.return_value.format.return_value = "test output"
        result = runner.invoke(c2p, ['.'])
        assert result.exit_code == 0
        assert "Failed to copy to clipboard" in result.output
        assert "Clipboard error" in result.output

def test_clipboard_with_config(tmp_path):
    """Test clipboard behavior with config file."""
    config_path = tmp_path / "config.ini"
    config_path.write_text("""
    [DEFAULT]
    clipboard = false
    """)
    
    # Test config overrides default clipboard behavior
    with patch('pyperclip.copy') as mock_copy, \
         patch('Codebase2Prompt.cli.get_codebase_files') as mock_files, \
         patch('Codebase2Prompt.cli.Formatter') as mock_formatter:
        mock_files.return_value = {}
        mock_formatter.return_value.format.return_value = "test output"
        result = runner.invoke(c2p, ['.', '--config', str(config_path)])
        assert result.exit_code == 0
        mock_copy.assert_not_called()
        
        # Test CLI flag overrides config
        result = runner.invoke(c2p, ['.', '--config', str(config_path), '--clipboard'])
        assert result.exit_code == 0
        mock_copy.assert_called_once()
