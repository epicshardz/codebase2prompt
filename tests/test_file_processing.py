import pytest
from pathlib import Path
from codebase2prompt.file_processor import FileProcessor

@pytest.fixture
def test_files_dir(tmp_path):
    test_dir = tmp_path / "test_files"
    test_dir.mkdir()
    
    # Create test files
    (test_dir / "test.lua").write_text("print('Hello Lua')")
    (test_dir / "test.html").write_text("<html><body>Test</body></html>")
    (test_dir / "test.js").write_text("console.log('Hello JS')")
    
    return test_dir

def test_process_lua_file(test_files_dir):
    """Test processing a Lua file"""
    processor = FileProcessor()
    result = processor.process_file(test_files_dir / "test.lua")
    assert result["language"] == "lua"
    assert "print('Hello Lua')" in result["content"]
    assert result["size"] > 0
    assert result["hash"] is not None

def test_process_html_file(test_files_dir):
    """Test processing an HTML file"""
    processor = FileProcessor()
    result = processor.process_file(test_files_dir / "test.html")
    assert result["language"] == "html"
    assert "<html><body>Test</body></html>" in result["content"]
    assert result["size"] > 0
    assert result["hash"] is not None

def test_process_js_file(test_files_dir):
    """Test processing a JavaScript file"""
    processor = FileProcessor()
    result = processor.process_file(test_files_dir / "test.js")
    assert result["language"] == "javascript"
    assert "console.log('Hello JS')" in result["content"]
    assert result["size"] > 0
    assert result["hash"] is not None

def test_invalid_file_handling(tmp_path):
    """Test handling of invalid/non-existent files"""
    invalid_file = tmp_path / "invalid.txt"
    
    processor = FileProcessor()
    result = processor.process_file(invalid_file)
    assert result is None

def test_large_file_handling(tmp_path):
    """Test handling of files exceeding size limit"""
    large_file = tmp_path / "large.txt"
    # Create a 11MB file
    large_file.write_text("a" * (11 * 1024 * 1024))
    
    processor = FileProcessor()
    result = processor.process_file(large_file)
    assert result is None

def test_binary_file_handling(tmp_path):
    """Test handling of binary files"""
    binary_file = tmp_path / "binary.bin"
    binary_file.write_bytes(b"\x00\x01\x02\x03")
    
    processor = FileProcessor()
    result = processor.process_file(binary_file)
    assert result["language"] is None
    assert result["content"] == "Binary file detected"
