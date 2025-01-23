"""CLI command definitions for Codebase2Prompt."""

import asyncio
from pathlib import Path
from typing import Optional
import pyperclip
import typer

def copy_to_clipboard(content: str):
    """Copy content to system clipboard."""
    try:
        pyperclip.copy(content)
    except Exception as e:
        raise typer.BadParameter(f"Failed to copy to clipboard: {str(e)}")


def analyze_command(
    path: Path = typer.Argument(
        ...,
        help="Path to analyze",
        exists=True,
        file_okay=True,
        dir_okay=True,
    ),
    recursive: bool = typer.Option(
        False,
        "--recursive",
        "-r",
        help="Recursively analyze directories",
    ),
    include_hidden: bool = typer.Option(
        False,
        "--hidden",
        "-H",
        help="Include hidden files and directories",
    ),
    output_format: str = typer.Option(
        "markdown",
        "--format",
        "-f",
        help="Output format (markdown, json, yaml)",
    ),
    visualize: bool = typer.Option(
        True,
        "--visualize/--no-visualize",
        help="Enable/disable real-time visualization",
    ),
    refresh_rate: float = typer.Option(
        0.1,
        "--refresh-rate",
        min=0.01,
        max=1.0,
        help="Visualization refresh rate in seconds (0.01-1.0)",
    ),
    show_progress: bool = typer.Option(
        True,
        "--progress/--no-progress",
        help="Show progress indicators during processing",
    ),
    verbose_visuals: bool = typer.Option(
        False,
        "--verbose-visuals",
        help="Show detailed visualizations with additional information",
    ),
    max_tree_depth: int = typer.Option(
        3,
        "--max-depth",
        min=1,
        max=10,
        help="Maximum depth for directory tree visualization",
    ),
    update_frequency: int = typer.Option(
        10,
        "--update-freq",
        min=1,
        max=100,
        help="Number of files processed between visualization updates",
    ),
    performance_threshold: float = typer.Option(
        0.8,
        "--perf-threshold",
        min=0.1,
        max=1.0,
        help="Performance threshold for reducing visualization updates (0.1-1.0)",
    ),
) -> None:
    """Analyze a codebase and generate a summary."""
    try:
        # Copy results to clipboard
        copy_to_clipboard("Analysis complete")
    except Exception as e:
        raise typer.Exit(1)
