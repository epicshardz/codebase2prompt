"""CLI command definitions for Codebase2Prompt."""

import asyncio
from pathlib import Path
from typing import Optional
import pyperclip
import typer

from Codebase2Prompt.documentation_generator import DocumentationGenerator
from Codebase2Prompt.ui import UIManager
from Codebase2Prompt.visualizer import ProjectVisualizer


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
    """Analyze a codebase and generate a summary with real-time visualization."""
    ui = UIManager()
    visualizer = None

    try:
        if visualize:
            try:
                visualizer = ProjectVisualizer(
                    console=ui.console,
                    refresh_rate=refresh_rate,
                    verbose=verbose_visuals,
                    max_tree_depth=max_tree_depth,
                    update_frequency=update_frequency,
                    performance_threshold=performance_threshold,
                )

                # Start live visualization
                ui.info("Starting real-time visualization...")
                asyncio.run(visualizer.start_live_display())

                # Create initial project structure visualization
                project_tree = asyncio.run(
                    visualizer.create_file_tree(
                        path, title=f"Analyzing: {path.name}", show_stats=verbose_visuals
                    )
                )
                asyncio.run(visualizer.update_display(project_tree))

                # Configure visualization settings
                visualizer.configure(
                    show_file_sizes=verbose_visuals,
                    show_analysis_stats=verbose_visuals,
                    show_processing_times=verbose_visuals,
                )
            except Exception as e:
                ui.warning(f"Visualization initialization failed: {e}")
                visualize = False

            # Setup progress tracking
            if show_progress:
                visualizer.add_progress_tracker(
                    total_files=100,  # Will be updated with actual count
                    description="Processing files",
                )

        # Perform analysis with visualization updates
        from Codebase2Prompt.parser import MultiLanguageParser
        from Codebase2Prompt.scanner import CodeScanner

        # Add language selection options
        languages = typer.Option(
            ["python", "javascript", "typescript"],
            "--languages",
            "-l",
            help="Languages to analyze (comma-separated)",
        )

        scanner = CodeScanner(
            root_path=path,
            recursive=recursive,
            include_hidden=include_hidden,
            progress_callback=visualizer.update_progress if show_progress else None,
        )

        parser = MultiLanguageParser(
            languages=languages,
            progress_callback=visualizer.update_progress if show_progress else None,
        )

        # Get initial file list
        files = scanner.scan()
        if show_progress:
            visualizer.update_total_files(len(files))

        # Process files with visualization updates
        results = []
        processed_files = 0
        for file_path in files:
            try:
                result = parser.parse_file(file_path)
                results.append(result)
                processed_files += 1

                if visualize:
                    try:
                        # Update visualization with rate limiting
                        if processed_files % 10 == 0 or verbose_visuals:
                            asyncio.run(visualizer.update_file_tree(file_path))

                        # Check for performance issues
                        if visualizer.is_overloaded():
                            ui.warning(
                                "Visualization performance degraded - reducing update frequency"
                            )
                            visualizer.reduce_update_frequency()
                            if visualizer.is_overloaded():
                                ui.warning("Disabling visualization due to performance constraints")
                                visualize = False
                                asyncio.run(visualizer.stop_live_display())

                    except Exception as e:
                        ui.warning(f"Visualization update failed: {e}")
                        visualize = False
                        asyncio.run(visualizer.stop_live_display())

            except Exception as e:
                ui.error(f"Error processing {file_path}: {e}")
                if show_progress:
                    visualizer.update_progress(1)  # Skip failed file

        # Copy results to clipboard
        output = "\n".join(str(r) for r in results)
        copy_to_clipboard(output)
        ui.success("Results copied to clipboard!")

    except Exception as e:
        ui.error(f"Visualization error: {e!s}")
        if visualizer:
            asyncio.run(visualizer.stop_live_display())
        raise typer.Exit(1)
    finally:
        if visualizer:
            asyncio.run(visualizer.stop_live_display())


def register_docs_commands(app: typer.Typer, ui_manager: UIManager) -> None:
    """Register documentation-related CLI commands."""

    docs_app = typer.Typer(help="Generate and manage project documentation.")
    app.add_typer(docs_app, name="docs")

    @docs_app.command("generate")
    def generate_docs(
        output: Path = typer.Option(
            Path("docs"),
            "--output",
            "-o",
            help="Output directory for documentation files",
        ),
        project_root: Optional[Path] = typer.Option(
            None,
            "--project",
            "-p",
            help="Project root directory (defaults to current)",
            exists=True,
            file_okay=False,
            dir_okay=True,
        ),
    ) -> None:
        """Generate comprehensive project documentation."""
        generator = DocumentationGenerator(ui_manager.console)
        try:
            # Confirm before generating docs
            if not ui_manager.config.silent and output.exists():
                if not ui_manager.prompt_confirm(
                    f"Documentation directory {output} already exists. Overwrite?", default=False
                ):
                    ui_manager.info("Documentation generation cancelled")
                    raise typer.Exit()

            files = generator.generate_docs(output, project_root)
            ui_manager.success(f"Documentation generated in {output}")
            for name, path in files.items():
                ui_manager.info(f"- {name}: {path}")
        except Exception as e:
            ui_manager.error(f"Error generating documentation: {e}")
            raise typer.Exit(1)

    @docs_app.command("update")
    def update_docs(
        docs_dir: Path = typer.Argument(
            ...,
            help="Documentation directory to update",
            exists=True,
            file_okay=False,
            dir_okay=True,
        ),
    ) -> None:
        """Update existing documentation files."""
        generator = DocumentationGenerator(ui_manager.console)
        try:
            # Confirm before updating
            if not ui_manager.config.silent:
                if not ui_manager.prompt_confirm(
                    "This will update documentation files. Continue?", default=True
                ):
                    ui_manager.info("Documentation update cancelled")
                    raise typer.Exit()

            generator.update_existing_docs(docs_dir)
            ui_manager.success(f"Documentation updated in {docs_dir}")
        except Exception as e:
            ui_manager.error(f"Error updating documentation: {e}")
            raise typer.Exit(1)
