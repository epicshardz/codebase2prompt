"""Code formatting and output generation."""

from pathlib import Path
from typing import Dict, List, Optional, Any
from rich.console import Console
import json
import yaml
from collections import defaultdict
from .file_processor import FileProcessor

class Formatter:
    """Handles formatting of codebase structure and content."""

    SUPPORTED_FORMATS = ["markdown", "json", "yaml"]

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.file_processor = FileProcessor()

    def format(self, files: Dict[Path, List[str]], output_format: str = "markdown", 
              max_lines: int = 10, no_codeblock: bool = False) -> str:
        """Format codebase files into a structured prompt.
        
        Args:
            files: Dictionary of files and their contents
            output_format: Format to output (markdown, json, or yaml)
            max_lines: Maximum number of lines to show per file
            no_codeblock: Whether to disable markdown code blocks
            
        Returns:
            Formatted output string
            
        Raises:
            ValueError: If output_format is not supported
        """
        # Process files using FileProcessor
        processed_files = {}
        for file_path, lines in files.items():
            processed = self.file_processor.process_file(
                file_path,
                no_codeblock=no_codeblock
            )
            if processed:
                processed_files[file_path] = processed['content'].split('\n')[:max_lines]
        if output_format not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {output_format}. Supported formats: {self.SUPPORTED_FORMATS}")
            
        if not files:
            return "No files found"
            
        if output_format == "markdown":
            return self._format_markdown(files, max_lines)
        elif output_format == "json":
            return self._format_json(files, max_lines)
        elif output_format == "yaml":
            return self._format_yaml(files, max_lines)

    def _build_tree(self, files: Dict[Path, List[str]]) -> dict:
        """Build a tree structure from file paths."""
        tree = defaultdict(dict)
        for file_path in files:
            current = tree
            # Get path relative to current working directory
            rel_path = file_path.relative_to(Path.cwd())
            parts = rel_path.parts
            for i, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = defaultdict(dict)
                current = current[part]
            current[parts[-1]] = "file"
        return tree

    def _format_tree(self, tree: dict, prefix: str = "", is_last: bool = True) -> List[str]:
        """Format tree structure with proper indentation and symbols."""
        lines = []
        items = list(tree.items())
        
        for i, (name, subtree) in enumerate(items):
            is_last_item = i == len(items) - 1
            
            # Determine the correct prefix for this line
            current_prefix = prefix + ("└── " if is_last_item else "├── ")
            
            # Add the current item
            lines.append(f"{current_prefix}{name}")
            
            # If this is a directory (dict), recursively format its contents
            if isinstance(subtree, dict):
                # Calculate the prefix for children
                extension = "    " if is_last_item else "│   "
                child_prefix = prefix + extension
                
                # Recursively format children
                lines.extend(self._format_tree(subtree, child_prefix, is_last_item))
                
        return lines

    def _format_markdown(self, files: Dict[Path, List[str]], max_lines: int) -> str:
        """Format files as markdown."""
        output = []
        
        # Add header
        output.append("# Codebase Structure")
        output.append("\n## Project Structure")
        output.append(f"\nDirectory: {Path.cwd()}")
        
        # Build and format tree structure
        if files:
            tree = self._build_tree(files)
            tree_lines = self._format_tree(tree)
            output.extend(tree_lines)
        else:
            output.append("*(No files found)*")
            
        # Add file contents
        output.append("\n## File Contents")
        if files:
            for file_path, lines in files.items():
                output.append(f"\n### {file_path}")
                output.append("```")
                if lines:
                    output.extend(lines[:max_lines])
                    if len(lines) > max_lines:
                        output.append("... (truncated)")
                else:
                    output.append("*(Empty file)*")
                output.append("```")
        else:
            output.append("\n*(No files to display)*")
            
        return "\n".join(output)

    def _format_json(self, files: Dict[Path, List[str]], max_lines: int) -> str:
        """Format files as JSON."""
        formatted = {
            "files": {
                str(path): {
                    "lines": lines[:max_lines],
                    "truncated": len(lines) > max_lines
                }
                for path, lines in files.items()
            }
        }
        return json.dumps(formatted, indent=2)

    def _format_yaml(self, files: Dict[Path, List[str]], max_lines: int) -> str:
        """Format files as YAML."""
        formatted = {
            "files": {
                str(path): {
                    "lines": lines[:max_lines],
                    "truncated": len(lines) > max_lines
                }
                for path, lines in files.items()
            }
        }
        return yaml.dump(formatted, default_flow_style=False)
