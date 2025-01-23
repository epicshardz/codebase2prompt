"""File processing functionality for codebase2prompt."""

from pathlib import Path
from datetime import datetime
import hashlib
from typing import Dict, Optional
import logging

from .utils.language_inference import infer_language

logger = logging.getLogger(__name__)

class FileProcessor:
    """Handles processing of files with various configurations."""
    
    def __init__(self, max_file_size: int = 10485760):  # 10MB default
        self.max_file_size = max_file_size
        
    def process_file(self, file_path: Path, no_codeblock: bool = False,
                   syntax_map: Optional[Dict] = None) -> Optional[Dict]:
        """
        Processes a given file to extract its metadata and content.
        
        Args:
            file_path: Path to the file to process
            no_codeblock: Whether to disable markdown code blocks
            syntax_map: Custom syntax mappings for language inference
            
        Returns:
            Dictionary containing file metadata and content, or None if processing fails
        """
        # Check if file exists
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return None
            
        # Validate file size
        try:
            file_size = file_path.stat().st_size
        except OSError as e:
            logger.warning(f"Could not access file {file_path}: {str(e)}")
            return None
        if file_size > self.max_file_size:
            logger.warning(f"File too large: {file_path} ({file_size} bytes)")
            return None
            
        # Collect metadata
        metadata = {
            "path": str(file_path),
            "extension": file_path.suffix,
            "size": file_size,
            "created": datetime.fromtimestamp(file_path.stat().st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "no_codeblock": no_codeblock,
        }
        
        # Process file content
        try:
            # First try reading as binary to check if it's a binary file
            with file_path.open("rb") as f:
                file_content = f.read()
                
            # First check if file is binary by attempting to decode
            try:
                text_content = file_content.decode('utf-8')
                # If successful and content is printable, process as text file
                if text_content.isprintable():
                    metadata["hash"] = hashlib.sha256(file_content).hexdigest()
                    metadata["language"] = infer_language(file_path.name, syntax_map or {})
                    metadata["content"] = text_content
                    return metadata
            except UnicodeDecodeError:
                pass
                
            # If we get here, treat as binary file
            metadata["hash"] = hashlib.sha256(file_content).hexdigest()
            metadata["language"] = None
            metadata["content"] = "Binary file detected"
            return metadata
                
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            return None
