import pytest
from pathlib import Path
from codebase2prompt.syntax_validator import (
    HTMLValidator,
    CSSValidator,
    JSValidator,
    LuaValidator,
    BinaryValidator
)

@pytest.fixture
def validators():
    return {
        'html': HTMLValidator(),
        'css': CSSValidator(),
        'js': JSValidator(),
        'lua': LuaValidator(),
        'binary': BinaryValidator()
    }

    def test_html_validation(validators):
        # Valid HTML
        valid_html = "<html><body></body></html>"
        validators['html'].validate(valid_html)
        
        # Minimal HTML
        minimal_html = "<html></html>"
        validators['html'].validate(minimal_html)
        
        # Invalid HTML
        with pytest.raises(SyntaxError):
            validators['html'].validate("not html")

    def test_css_validation(validators):
        # Valid CSS
        valid_css = "body { color: red; }"
        validators['css'].validate(valid_css)
        
        # Minimal CSS
        minimal_css = "a {}"
        validators['css'].validate(minimal_css)
        
        # Invalid CSS
        with pytest.raises(SyntaxError):
            validators['css'].validate("not css")

def test_js_validation(validators):
    # Valid JavaScript
    valid_js = "function test() { return true; }"
    validators['js'].validate(valid_js)
    
    # Invalid JavaScript
    invalid_js = "function test() { return true"
    with pytest.raises(SyntaxError):
        validators['js'].validate(invalid_js)

def test_lua_validation(validators):
    # Valid Lua
    valid_lua = "function test() return true end"
    validators['lua'].validate(valid_lua)
    
    # Invalid Lua
    invalid_lua = "function test() return true"
    with pytest.raises(SyntaxError):
        validators['lua'].validate(invalid_lua)

def test_binary_validation(validators):
    # Binary validator should always pass
    binary_data = b"\x00\x01\x02\x03"
    validators['binary'].validate(binary_data)
