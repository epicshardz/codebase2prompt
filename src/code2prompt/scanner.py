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
        # Replace ** with a pattern that matches zero or more directory components
        pattern = pattern.replace('**', '__DOUBLEWILDCARD__')
        # Convert to regex using fnmatch
        regex = translate(pattern)
        # Replace the marker with a pattern that matches zero or more directory components
        # [^/\\]* matches any characters except / and \
        # (?:/|\\\\).* matches / or \ followed by any characters
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

        # Check if path contains venv directory
        # if "venv" in Path(path_str).parts:
        #     logger.debug(f"Excluding {path_str} - in venv directory")
        #     return False

        # Add trailing slash for directories to match patterns like **venv/**
        if entry.is_dir(follow_symlinks=False):
            path_str += '/'
            logger.debug(f"Checking directory: {path_str}")
            # For directories, we only need to check exclude patterns
            if self._matches_pattern(path_str, self.exclude_patterns, "exclude"):
                # logger.debug(f"Excluding directory {path_str} based on exclude patterns")
                return False
            return True

        # For files, check if it's a valid file first
        if not entry.is_file(follow_symlinks=False):
            return False

        # Check if file is empty
        try:
            if os.path.getsize(entry.path) == 0:
                # logger.debug(f"Skipping empty file: {path_str}")
                return False
        except OSError:
            # logger.debug(f"Skipping inaccessible file: {path_str}")
            return False

        # Check exclude patterns first for files
        if self._matches_pattern(path_str, self.exclude_patterns, "exclude"):
            # logger.debug(f"Excluding file {path_str} based on exclude patterns")
            return False

        # Finally check include patterns
        included = self._matches_pattern(path_str, self.include_patterns, "include")
        # if included:
        #     # logger.debug(f"Including file: {path_str}")
        # else:
        #     # logger.debug(f"Excluding file {path_str} - doesn't match include patterns")
            
        return included

    def _scan_directory(self, path: Path) -> Iterator[Path]:
        """Scan a single directory for files.

        Args:
            path: Directory to scan

        Yields:
            Path objects for matching files
        """
        try:
            for entry in os.scandir(str(path)):
                try:
                    if entry.is_file(follow_symlinks=False):
                        try:
                            # Check if file is text and decodable
                            with open(entry.path, 'r', encoding='utf-8') as f:
                                f.read()
                            if self._should_include(entry):
                                yield Path(entry.path)
                        except UnicodeDecodeError:
                            continue
                        except Exception:
                            continue
                    elif entry.is_dir(follow_symlinks=False):
                        # Skip venv directory entirely
                        if "venv" in Path(entry.path).parts:
                            # logger.debug(f"Skipping venv directory: {entry.path}")
                            continue
                        # Only recurse if directory isn't excluded
                        path_str = str(entry.path)
                        if not self._matches_pattern(path_str, self.exclude_patterns, "exclude"):
                            yield from self._scan_directory(Path(entry.path))
                except Exception:
                    continue
        except (PermissionError, Exception):
            return

    def scan(self, path: Path) -> Iterator[Path]:
        """Scan a directory for files matching the patterns.

        Args:
            path: Directory path to scan

        Yields:
            Path objects for matching files

        Raises:
            NotADirectoryError: If path is not a directory
        """
        if not path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {path}")

        # Skip if path itself contains venv
        if "venv" in path.parts:
            # logger.debug(f"Skipping venv directory path: {path}")
            return

        yield from self._scan_directory(path)


def scan_directory(path: Path, include_patterns=None, exclude_patterns=None) -> Iterator[Path]:
    """Scan a directory for files matching the patterns.

    Args:
        path: Directory path to scan
        include_patterns: List of glob patterns to include files
        exclude_patterns: List of glob patterns to exclude files

    Yields:
        Path objects for matching files
    """
    # Convert glob patterns to regex patterns
    include_regex = [glob_to_regex(p) for p in (include_patterns or [])]
    exclude_regex = [glob_to_regex(p) for p in (exclude_patterns or [])]
    
    scanner = FileScanner(include_regex, exclude_regex)
    return scanner.scan(path)
