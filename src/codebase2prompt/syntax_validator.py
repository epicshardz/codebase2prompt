"""Syntax validation for various file types."""

import html.parser
import cssutils
import esprima
import lupa
from typing import Optional, Tuple

class SyntaxValidator:
    """Base class for syntax validation."""
    
    def validate(self, content: str) -> None:
        """Validate syntax, raising SyntaxError if invalid."""
        raise NotImplementedError()

class HTMLValidator(SyntaxValidator):
    """HTML syntax validator."""
    
    def validate(self, content: str) -> None:
        # Basic check that content appears to be HTML
        if not content.strip():
            raise SyntaxError("Empty content")
        if '<' not in content or '>' not in content:
            raise SyntaxError("Content does not appear to be HTML")

class CSSValidator(SyntaxValidator):
    """CSS syntax validator."""
    
    def validate(self, content: str) -> None:
        # Basic check that content appears to be CSS
        if not content.strip():
            raise SyntaxError("Empty content")
        if '{' not in content or '}' not in content:
            raise SyntaxError("Content does not appear to be CSS")

class JSValidator(SyntaxValidator):
    """JavaScript syntax validator."""
    
    def validate(self, content: str) -> None:
        try:
            esprima.parseScript(content)
        except Exception as e:
            raise SyntaxError(f"JavaScript validation error: {str(e)}")

class LuaValidator(SyntaxValidator):
    """Lua syntax validator."""
    
    def __init__(self):
        self.lua = lupa.LuaRuntime()
        
    def validate(self, content: str) -> None:
        try:
            self.lua.execute(content)
        except Exception as e:
            raise SyntaxError(f"Lua validation error: {str(e)}")

class BinaryValidator(SyntaxValidator):
    """Binary file validator."""
    
    def validate(self, content: str) -> None:
        try:
            # Basic binary validation
            if not isinstance(content, bytes):
                raise SyntaxError("Invalid binary content")
        except Exception as e:
            raise SyntaxError(f"Binary validation error: {str(e)}")
