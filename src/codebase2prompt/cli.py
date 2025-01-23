"""Command-line interface for Codebase2Prompt."""

import logging
import sys
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
    default_types = defaults.get("default_include_types", "*.py,*.js,*.ts,*.html,*.css").split(",")
    
    # If include is '*', use default types unless overridden
    if config_include == ["*"]:
        merged["include"] = [e.strip() for e in default_types if e.strip()]
    else:
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
    
    # Handle clipboard - CLI flags override config, but config is used if no flags
    config_clipboard = defaults.get("clipboard", "true").lower() == "true"
    merged["clipboard"] = config_clipboard  # Default to config value
    
    # CLI flags override config
    if cli_args.get("enable_clipboard"):
        merged["clipboard"] = True
    if cli_args.get("no_clipboard"):
        merged["clipboard"] = False
    
    # Handle output format
    merged["output_format"] = cli_args.get("output_format") or defaults.get("output_format", "markdown")
    
    # Handle line numbers
    config_line_numbers = defaults.get("line_numbers", "false").lower() == "true"
    merged["line_numbers"] = cli_args.get("line_numbers", config_line_numbers)
    
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
    ),
    line_numbers: bool = typer.Option(
        False,
        "--line-numbers",
        help="Include line numbers in the output"
    )
) -> None:
    """Generate a prompt from codebase structure and content."""
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    try:
        # Handle config creation
        if create_config:
            if config.exists():
                confirm = typer.confirm(
                    f"Config file {config} already exists. Overwrite?",
                    default=False
                )
                if not confirm:
                    typer.echo("Aborted config creation", err=True)
                    raise typer.Abort()
            
            try:
                create_default_config(config)
                typer.echo(f"Created new config file at {config}")
                raise typer.Exit()
            except Exception as e:
                typer.echo(typer.style(f"Error creating config: {str(e)}", fg="red"), err=True)
                raise typer.Exit(code=1)

        # Load config file if it exists
        config_values = {"DEFAULT": DEFAULT_CONFIG}
        if config.exists():
            try:
                config_values = load_config(config)
            except Exception as e:
                typer.echo(
                    typer.style(f"Error loading config: {str(e)}", fg="red"),
                    err=True
                )
                raise typer.Exit(code=1)
        
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
        
        # Validate clipboard config
        if not isinstance(args["clipboard"], bool):
            args["clipboard"] = str(args["clipboard"]).lower() == "true"
        
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
    except typer.Exit as e:
        if hasattr(e, 'exit_code'):
            raise typer.Exit(code=e.exit_code)  # Preserve exit code when re-raising
        else:
            raise  # Re-raise the original exception if no exit_code
    except typer.Abort:
        raise typer.Exit(code=1)  # Convert Abort to Exit with code 1
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
