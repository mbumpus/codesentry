"""CS002: Placeholder Code in Production Pattern"""

import ast
import re
from typing import Optional

from ..models import Issue, Severity, TeachingInfo
from .base import BasePattern


class PlaceholderCodePattern(BasePattern):
    """Detect TODO/FIXME with placeholder implementations"""

    # Regex to find TODO/FIXME/HACK comments
    TODO_PATTERN = re.compile(r'#\s*(TODO|FIXME|HACK|XXX)\b', re.IGNORECASE)

    # Decorators that legitimately require empty bodies
    LEGITIMATE_STUB_DECORATORS = frozenset({
        'abstractmethod',
        'overload',
        'property',
        'staticmethod',
        'classmethod',
        # Also handle fully qualified names
        'abc.abstractmethod',
        'typing.overload',
        'typing_extensions.overload',
    })

    # Base classes that legitimately use stub methods
    PROTOCOL_BASES = frozenset({
        'Protocol',
        'ABC',
        'typing.Protocol',
        'typing_extensions.Protocol',
        'abc.ABC',
    })

    @property
    def id(self) -> str:
        return "CS002"

    @property
    def name(self) -> str:
        return "placeholder-code-in-production"

    @property
    def category(self) -> str:
        return "ai-generated-signature"

    @property
    def severity(self) -> Severity:
        return Severity.ERROR

    @property
    def description(self) -> str:
        return "TODO/FIXME comments paired with placeholder implementations"

    def get_teaching(self) -> TeachingInfo:
        return TeachingInfo(
            what="You have placeholder code that was never implemented.",
            why="LLMs often generate function stubs with TODO comments, expecting you to "
                "fill them in. Shipping these means silent failures or crashes in production. "
                "It's also a sign of copy-paste without review.",
            fix="Implement the function, remove it if unused, or raise a clear custom "
                "exception if intentionally incomplete.",
            spot_it_yourself="Run 'grep -rn \"TODO\\|FIXME\" *.py' and check each hit. "
                            "Is there actual implementation below the comment? "
                            "Set up pre-commit hooks to catch these.",
            example_bad="""def calculate_tax(amount, region):
    # TODO: implement tax calculation
    pass""",
            example_good="""def calculate_tax(amount: float, region: str) -> float:
    tax_rates = {'US': 0.08, 'UK': 0.20, 'DE': 0.19}
    if region not in tax_rates:
        raise UnsupportedRegionError(f'No tax rate for {region}')
    return amount * tax_rates[region]"""
        )

    def analyze(self, tree: ast.AST, source_lines: list[str], source: str) -> list[Issue]:
        issues = []

        # Find lines with TODO/FIXME comments
        todo_lines = self._find_todo_lines(source_lines)

        # Build a map of classes that inherit from Protocol/ABC
        protocol_classes = self._find_protocol_classes(tree)

        # Check functions for placeholder bodies
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Skip legitimate stub patterns (BUG-001 fix)
                if self._is_legitimate_stub(node, tree, protocol_classes):
                    continue

                if self._is_placeholder_function(node, todo_lines):
                    snippet = self._get_snippet(source_lines, node.lineno, context=2)
                    issues.append(self._create_issue(
                        line=node.lineno,
                        col=node.col_offset,
                        snippet=snippet,
                        end_line=node.end_lineno
                    ))

        return issues

    def _find_todo_lines(self, source_lines: list[str]) -> set[int]:
        """Find all line numbers containing TODO/FIXME comments"""
        todo_lines = set()
        for i, line in enumerate(source_lines, start=1):
            if self.TODO_PATTERN.search(line):
                todo_lines.add(i)
        return todo_lines

    def _find_protocol_classes(self, tree: ast.AST) -> set[str]:
        """Find class names that inherit from Protocol or ABC"""
        protocol_classes = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    base_name = self._get_name(base)
                    if base_name in self.PROTOCOL_BASES:
                        protocol_classes.add(node.name)
                        break

        return protocol_classes

    def _get_name(self, node: ast.expr) -> str:
        """Extract name from an AST node (handles Name and Attribute)"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            # Handle typing.Protocol, abc.ABC, etc.
            value_name = self._get_name(node.value)
            if value_name:
                return f"{value_name}.{node.attr}"
            return node.attr
        return ""

    def _get_decorator_names(self, node: ast.FunctionDef) -> set[str]:
        """Extract all decorator names from a function"""
        names = set()
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                names.add(decorator.id)
            elif isinstance(decorator, ast.Attribute):
                # Handle @abc.abstractmethod style
                names.add(self._get_name(decorator))
                names.add(decorator.attr)  # Also add just the attr name
            elif isinstance(decorator, ast.Call):
                # Handle @decorator() style
                if isinstance(decorator.func, ast.Name):
                    names.add(decorator.func.id)
                elif isinstance(decorator.func, ast.Attribute):
                    names.add(self._get_name(decorator.func))
                    names.add(decorator.func.attr)
        return names

    def _get_enclosing_class(self, func_node: ast.FunctionDef, tree: ast.AST) -> Optional[ast.ClassDef]:
        """Find the class that contains this function, if any"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if item is func_node:
                        return node
                    # Check for nested definitions
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        continue
        return None

    def _is_legitimate_stub(self, node: ast.FunctionDef, tree: ast.AST, protocol_classes: set[str]) -> bool:
        """
        Check if this function stub is a legitimate Python pattern.

        Legitimate stubs include:
        - @abstractmethod decorated methods
        - @overload decorated type stubs
        - Methods in Protocol classes
        - Methods in ABC classes
        - @property, @staticmethod, @classmethod in abstract contexts
        """
        decorator_names = self._get_decorator_names(node)

        # Check for legitimate stub decorators
        if decorator_names & self.LEGITIMATE_STUB_DECORATORS:
            return True

        # Check if method is inside a Protocol or ABC class
        enclosing_class = self._get_enclosing_class(node, tree)
        if enclosing_class and enclosing_class.name in protocol_classes:
            return True

        return False

    def _is_placeholder_function(self, node: ast.FunctionDef, todo_lines: set[int]) -> bool:
        """
        Check if function has placeholder body WITH TODO nearby.

        BUG-002 fix: Only flag if TODO/FIXME is present within 3 lines.
        The spec says "TODO/FIXME comments paired with placeholder implementations".
        """
        body = node.body

        # Skip docstring if present
        if body and isinstance(body[0], ast.Expr):
            if isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
                body = body[1:]

        if not body:
            # Empty body after docstring - check for TODO
            return self._has_todo_nearby(node, todo_lines)

        # Check if body is just pass, ellipsis, or NotImplementedError
        is_placeholder = False

        if len(body) == 1:
            stmt = body[0]
            # pass statement
            if isinstance(stmt, ast.Pass):
                is_placeholder = True
            # Ellipsis (...)
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                if stmt.value.value is ...:
                    is_placeholder = True
            # raise NotImplementedError
            elif isinstance(stmt, ast.Raise):
                if self._is_not_implemented_error(stmt):
                    is_placeholder = True

        if not is_placeholder:
            return False

        # BUG-002 FIX: Only flag if TODO/FIXME is present nearby
        # This is the key change - we no longer flag stubs without TODO
        return self._has_todo_nearby(node, todo_lines)

    def _has_todo_nearby(self, node: ast.FunctionDef, todo_lines: set[int]) -> bool:
        """Check for TODO/FIXME within 3 lines of function definition"""
        func_start = node.lineno
        func_end = node.end_lineno or func_start + 5

        # Check from 1 line before the function to end of function
        for line_no in range(max(1, func_start - 1), func_end + 1):
            if line_no in todo_lines:
                return True

        return False

    def _is_not_implemented_error(self, raise_node: ast.Raise) -> bool:
        """Check if raise statement is raising NotImplementedError"""
        exc = raise_node.exc
        if exc is None:
            return False

        # raise NotImplementedError
        if isinstance(exc, ast.Name) and exc.id == "NotImplementedError":
            return True

        # raise NotImplementedError(...)
        if isinstance(exc, ast.Call):
            if isinstance(exc.func, ast.Name) and exc.func.id == "NotImplementedError":
                return True

        return False
