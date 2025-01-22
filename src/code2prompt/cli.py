"""Command-line interface for Codebase2Prompt."""

import logging
import typer
import pyperclip
from pathlib import Path
from typing import Dict, List, Optional
from .config import load_config, create_default_config, DEFAULT_CONFIG
from .formatter import Formatter

cli = typer.Typer(name="c2p", help="Generate a prompt from codebase structure and content")

def version_callback(value: bool):
    if value:
        from . import __version__
        typer.echo(f"c2p version: {__version__}")
        raise typer.Exit()

def merge_config_with_cli(config: Dict[str, Dict[str, str]], cli_args: dict) -> dict:
    """Merge configuration values with CLI arguments."""
    merged = {}
    defaults = config.get("DEFAULT", {})
    
    # Handle include patterns
    config_include = defaults.get("include", "").split(",")
    merged["include"] = [e.strip() for e in config_include if e.strip()]
    
    # Handle exclude patterns
    config_exclude = defaults.get("exclude", "").split(",")
    cli_exclude = list(cli_args.get("exclude", []))
    merged["exclude"] = cli_exclude + [e.strip() for e in config_exclude if e.strip()]
    
    # Handle max file size
    try:
        merged["max_file_size"] = int(defaults.get("max_file_size", 1048576))
    except ValueError:
        merged["max_file_size"] = 1048576  # Default if invalid
    
    # Handle clipboard - CLI flags take precedence over config
    config_clipboard = defaults.get("clipboard", "true").lower() == "true"
    if cli_args.get("enable_clipboard"):
        merged["clipboard"] = True
    elif cli_args.get("no_clipboard"):
        merged["clipboard"] = False
    else:
        merged["clipboard"] = config_clipboard
    
    # Handle output format
    merged["output_format"] = cli_args.get("output_format") or defaults.get("output_format", "markdown")
    
    return merged

@cli.command()
def main(
    path: Path = typer.Argument(
        Path.cwd(),
        help="Path to codebase directory"
    ),
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit"
    ),
    create_config: bool = typer.Option(
        False,
        "--create-config",
        help="Create a new config file with default values"
    ),
    exclude: List[str] = typer.Option(
        [],
        "--exclude",
        help="Additional directories or files to exclude from processing"
    ),
    no_clipboard: bool = typer.Option(
        False,
        "--no-clipboard",
        help="Disable automatic copying to clipboard"
    ),
    enable_clipboard: bool = typer.Option(
        False,
        "--clipboard",
        help="Enable automatic copying to clipboard"
    ),
    config: Path = typer.Option(
        "config.ini",
        "--config",
        help="Path to configuration file (default: config.ini)"
    ),
    output_format: Optional[str] = typer.Option(
        None,
        "--output-format",
        help="Override output format (markdown, json, or yaml)"
    )
) -> None:
    """Generate a prompt from codebase structure and content."""
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    try:
        # Use default config
        config_values = {"DEFAULT": DEFAULT_CONFIG}
        
        # Convert typer argument to Path
        if hasattr(path, 'default'):
            scan_path = Path(str(path.default))
        else:
            scan_path = Path(str(path))
        scan_path = scan_path.resolve()
        exclude_list = exclude if isinstance(exclude, list) else []
        no_clip = no_clipboard if isinstance(no_clipboard, bool) else False
        enable_clip = enable_clipboard if isinstance(enable_clipboard, bool) else False
        out_format = output_format if isinstance(output_format, str) else None
        
        # Merge config with CLI args
        args = merge_config_with_cli(config_values, {
            "exclude": exclude_list,
            "no_clipboard": no_clip,
            "enable_clipboard": enable_clip,
            "output_format": out_format
        })
        
        formatter = Formatter()
        files = get_codebase_files(
            scan_path,
            include=args["include"],
            exclude=args["exclude"],
            max_file_size=args["max_file_size"]
        )
        
        output = formatter.format(
            files,
            output_format=args["output_format"]
        )
        
        typer.echo(output)
        
        # Handle clipboard copy if enabled
        if args["clipboard"]:
            try:
                pyperclip.copy(output)
                typer.echo(typer.style("Output copied to clipboard!", fg="green"))
            except pyperclip.PyperclipException as e:
                typer.echo(
                    typer.style("Failed to copy to clipboard: No clipboard system available", fg="red"),
                    err=True
                )
            except Exception as e:
                typer.echo(
                    typer.style(f"Failed to copy to clipboard: {str(e)}", fg="red"),
                    err=True
                )
    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(typer.style(f"Error: {str(e)}", fg="red"), err=True)
        raise typer.Exit(code=1)

def get_codebase_files(path: Path, include: List[str], exclude: List[str], max_file_size: int) -> dict:
    """Get codebase files while respecting inclusions and exclusions."""
    from .scanner import scan_directory
    from .parser import parse_files
    
    try:
        files = list(scan_directory(path, include, exclude))
        return parse_files(files, max_lines=max_file_size)
    except Exception as e:
        typer.echo(typer.style(f"Error scanning files: {str(e)}", fg="red"), err=True)
        return {}
