from dataclasses import dataclass
from typing import Optional

import esprima


@dataclass
class JavaScriptFunction:
    name: str
    parameters: list[str]
    return_type: Optional[str]
    docstring: Optional[str]
    decorators: list[str]
    start_line: int
    end_line: int


class JavaScriptParser:
    def __init__(self):
        self.functions: list[JavaScriptFunction] = []

    def parse(self, code: str) -> list[JavaScriptFunction]:
        """Parse JavaScript/TypeScript code and extract function information"""
        try:
            parsed = esprima.parseScript(code, {"loc": True, "comment": True})
            self._traverse(parsed)
            return self.functions
        except esprima.Error as e:
            raise ValueError(f"JavaScript parsing error: {e!s}") from e

    def _traverse(self, node):
        """Recursively traverse the AST and extract function definitions"""
        if node.type == "FunctionDeclaration":
            self._process_function(node)
        elif node.type == "VariableDeclaration":
            for decl in node.declarations:
                if decl.init and decl.init.type == "FunctionExpression":
                    self._process_function(decl.init, name=decl.id.name)

        # Recursively process child nodes
        for child in getattr(node, "body", []):
            self._traverse(child)
        for child in getattr(node, "declarations", []):
            self._traverse(child)
        for child in getattr(node, "expression", []):
            self._traverse(child)

    def _process_function(self, node, name: Optional[str] = None):
        """Extract information from a function node"""
        func_name = name or getattr(node.id, "name", "anonymous")
        params = [param.name for param in node.params]

        # Extract docstring from leading comments
        docstring = None
        if hasattr(node, "leadingComments"):
            for comment in node.leadingComments:
                if comment.type == "Block" and comment.value.strip().startswith("*"):
                    docstring = comment.value.strip()
                    break

        # Get location information
        start_line = node.loc.start.line
        end_line = node.loc.end.line

        self.functions.append(
            JavaScriptFunction(
                name=func_name,
                parameters=params,
                return_type=None,  # TypeScript types would require additional handling
                docstring=docstring,
                decorators=[],  # Decorators would require additional handling
                start_line=start_line,
                end_line=end_line,
            )
        )
