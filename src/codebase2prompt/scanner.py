"""File scanner module for Codebase2Prompt."""

import logging
import os
from collections.abc import Iterator
from pathlib import Path
from re import Pattern, compile
from fnmatch import translate

logger = logging.getLogger(__name__)

def glob_to_regex(pattern: str) -> Pattern[str]:
    """Convert a glob pattern to a regex pattern.
    
    Args:
        pattern: Glob pattern (e.g. *.py, **venv/**)
        
    Returns:
        Compiled regex pattern
    """
    # Handle **/ pattern for recursive directory matching
    if '**' in pattern:
        pattern = pattern.replace('**', '__DOUBLEWILDCARD__')
        regex = translate(pattern)
        regex = regex.replace('__DOUBLEWILDCARD__', '(?:[^/\\\\]*(?:/|\\\\\\\\))*[^/\\\\]*')
        return compile(regex)
    return compile(translate(pattern))


class FileScanner:
    """Scans directories and files based on filters."""

    def __init__(
        self,
        include_patterns: list[Pattern[str]] | None = None,
        exclude_patterns: list[Pattern[str]] | None = None,
    ) -> None:
        """Initialize the file scanner.

        Args:
            include_patterns: List of regex patterns to include files
            exclude_patterns: List of regex patterns to exclude files
        """
        self.include_patterns = include_patterns or []
        self.exclude_patterns = exclude_patterns or []

    def _matches_pattern(
        self, path_str: str, patterns: list[Pattern[str]], pattern_type: str
    ) -> bool:
        """Check if a path matches any of the given patterns.

        Args:
            path_str: String representation of path
            patterns: List of regex patterns to match against
            pattern_type: Type of pattern ('include' or 'exclude')

        Returns:
            True if the path matches any pattern, False otherwise
        """
        if not patterns:
            return pattern_type == "include"

        for pattern in patterns:
            try:
                if pattern.search(path_str):
                    return True
            except Exception:
                continue

        return False

    def _should_include(self, entry: os.DirEntry) -> bool:
        """Determine if a directory entry should be included based on patterns.

        Args:
            entry: Directory entry to check

        Returns:
            True if the entry should be included, False otherwise
        """
        path_str = str(entry.path)

        if entry.is_dir(follow_symlinks=False):
            path_str += '/'
            logger.debug(f"Checking directory: {path_str}")
            if self._matches_pattern(path_str, self.exclude_patterns, "exclude"):
                return False
            return True

        if not entry.is_file(follow_symlinks=False):
            return False

        try:
            if os.path.getsize(entry.path) == 0:
                return False
        except OSError:
            return False

        # Check if this is a root directory file
        is_root_file = len(Path(path_str).relative_to(Path(path_str).anchor).parts) == 1
        
        # Always include root directory files unless explicitly excluded
        if is_root_file:
            return not self._matches_pattern(path_str, self.exclude_patterns, "exclude")

        # For non-root files, apply both include and exclude patterns
        if self._matches_pattern(path_str, self.exclude_patterns, "exclude"):
            return False
            
        return self._matches_pattern(path_str, self.include_patterns, "include")

    def _scan_directory(self, path: Path) -> Iterator[Path]:
        """Scan a single directory for files.

        Args:
            path: Directory to scan

        Yields:
            Path objects for matching files
        """
        try:
            # First process files in the current directory
            for entry in os.scandir(str(path)):
                try:
                    if entry.is_file(follow_symlinks=False):
                        try:
                            with open(entry.path, 'r', encoding='utf-8') as f:
                                f.read()
                            if self._should_include(entry):
                                yield Path(entry.path)
                        except UnicodeDecodeError:
                            continue
                        except Exception:
                            continue
                    elif entry.is_dir(follow_symlinks=False):
                        # Only skip actual virtual environment directories
                        if Path(entry.path).name == "venv":
                            continue
                        path_str = str(entry.path)
                        if not self._matches_pattern(path_str, self.exclude_patterns, "exclude"):
                            yield from self._scan_directory(Path(entry.path))
                except Exception:
                    continue
        except (PermissionError, Exception):
            return

    def scan(self, path: Path) -> Iterator[Path]:
        """Scan a directory or file for matching patterns.

        Args:
            path: Path to scan (can be directory or file)

        Yields:
            Path objects for matching files

        Raises:
            NotADirectoryError: If path is not a directory or file
        """
        if path.is_file():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    f.read()
                if self._should_include(os.scandir(path.parent).__next__()):
                    yield path
            except (UnicodeDecodeError, OSError):
                return
        elif path.is_dir():
            if "venv" in path.parts:
                return
            yield from self._scan_directory(path)
        else:
            raise NotADirectoryError(f"Path is not a directory or file: {path}")


def scan_directory(path: Path, include_patterns=None, exclude_patterns=None) -> Iterator[Path]:
    """Scan a directory for files matching the patterns.

    Args:
        path: Directory path to scan
        include_patterns: List of glob patterns to include files
        exclude_patterns: List of glob patterns to exclude files

    Yields:
        Path objects for matching files
    """
    include_regex = [glob_to_regex(p) for p in (include_patterns or [])]
    exclude_regex = [glob_to_regex(p) for p in (exclude_patterns or [])]
    
    scanner = FileScanner(include_regex, exclude_regex)
    return scanner.scan(path)
