"""Simplified code parser for Codebase2Prompt."""

import ast
from pathlib import Path
from typing import Iterator

class SimpleParser:
    """Simplified parser that extracts class/function names and hierarchy."""
    
    def __init__(self, max_lines: int = 5):
        """Initialize the parser.
        
        Args:
            max_lines: Maximum number of lines to show per definition
        """
        self.max_lines = max_lines

    def parse_files(self, files: list[Path]) -> dict[Path, list[str]]:
        """Parse multiple files and return their structure.
        
        Args:
            files: List of file paths to parse
            
        Returns:
            Dictionary mapping files to their hierarchical structure
        """
        return {file: self.parse_file(file) for file in files}

    def parse_file(self, file: Path) -> list[str]:
        """Parse a single file and return its structure.
        
        Args:
            file: Path to the file to parse
            
        Returns:
            List of hierarchical definitions
        """
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            return list(self._extract_definitions(content, file))
        except UnicodeDecodeError:
            return [f"# Unable to parse {file.name}: Binary file"]
        except Exception as e:
            return [f"# Error parsing {file.name}: {str(e)}"]

    def _extract_definitions(self, content: str, file: Path) -> Iterator[str]:
        """Extract class/function definitions from content.
        
        Args:
            content: File content to parse
            file: Path to the file being parsed
            
        Yields:
            Hierarchical definitions as strings
        """
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    yield self._format_definition(node)
        except SyntaxError:
            yield f"# Syntax error in {file.name}"

    def _format_definition(self, node: ast.AST) -> str:
        """Format a definition with proper indentation.
        
        Args:
            node: AST node to format
            
        Returns:
            Formatted definition string
        """
        indent = "    " * (len(self._get_parents(node)) - 1)
        return f"{indent}{node.name} (lines {node.lineno}-{node.end_lineno})"

    def _get_parents(self, node: ast.AST) -> list[ast.AST]:
        """Get parent nodes for proper indentation.
        
        Args:
            node: AST node to get parents for
            
        Returns:
            List of parent nodes
        """
        parents = []
        while hasattr(node, 'parent'):
            node = node.parent
            parents.append(node)
        return parents


def parse_files(files: list[Path], max_lines: int = 5) -> dict[Path, list[str]]:
    """Parse multiple files and return their structure.
    
    Args:
        files: List of file paths to parse
        max_lines: Maximum number of lines to show per definition
        
    Returns:
        Dictionary mapping files to their hierarchical structure
    """
    parser = SimpleParser(max_lines)
    return parser.parse_files(files)
