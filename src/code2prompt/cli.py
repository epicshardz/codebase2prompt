"""Command-line interface for Code2Prompt."""

import click
from rich.console import Console

console = Console()

@click.group()
@click.version_option()
def main() -> None:
    """Generate project architecture and file summaries optimized for LLMs."""
    pass

@main.command()
@click.argument('path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--copy/--no-copy', default=True, help='Automatically copy output to clipboard')
def analyze(path: str, copy: bool) -> None:
    """Analyze a project directory and generate a summary."""
    console.print(f"[bold green]Analyzing project at:[/] {path}")
    # Implementation will be added in future tasks

if __name__ == '__main__':
    main()
