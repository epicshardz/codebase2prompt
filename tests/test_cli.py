"""Tests for the command-line interface."""

from click.testing import CliRunner

from code2prompt.cli import main

def test_cli_version():
    """Test that the CLI version command works."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.output.lower()

def test_analyze_command_help():
    """Test that the analyze command help text is displayed."""
    runner = CliRunner()
    result = runner.invoke(main, ["analyze", "--help"])
    assert result.exit_code == 0
    assert "Analyze a project directory" in result.output
