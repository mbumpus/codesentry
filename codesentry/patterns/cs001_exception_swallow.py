"""CS001: Generic Exception Swallow Pattern"""

import ast

from ..models import Issue, Severity, TeachingInfo
from .base import BasePattern


class ExceptionSwallowPattern(BasePattern):
    """Detect broad exceptions being silently swallowed"""

    @property
    def id(self) -> str:
        return "CS001"

    @property
    def name(self) -> str:
        return "generic-exception-swallow"

    @property
    def category(self) -> str:
        return "ai-generated-signature"

    @property
    def severity(self) -> Severity:
        return Severity.WARNING

    @property
    def description(self) -> str:
        return "Catching broad exceptions and silently ignoring them"

    def get_teaching(self) -> TeachingInfo:
        return TeachingInfo(
            what="You're catching all exceptions and silently swallowing them.",
            why="This hides bugs, masks crashes, and makes debugging nearly impossible. "
                "If something fails, you'll never know. LLMs often generate this pattern "
                "because it 'prevents errors' in the most superficial way.",
            fix="Catch specific exceptions you can handle. Re-raise or log with traceback for unexpected ones.",
            spot_it_yourself="Search for 'except Exception' and 'except:' in your codebase. "
                            "Ask: 'What specific error am I handling here?' If you can't answer, "
                            "you're probably swallowing bugs.",
            example_bad="""try:
    data = fetch_user(id)
except Exception:
    pass  # User not found? Network error? Bug? Who knows!""",
            example_good="""try:
    data = fetch_user(id)
except UserNotFoundError:
    return None  # Expected case, handled explicitly
except NetworkError as e:
    logger.warning(f'Network issue: {e}')
    raise  # Let caller decide retry strategy"""
        )

    def analyze(self, tree: ast.AST, source_lines: list[str], source: str) -> list[Issue]:
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if self._is_swallowing_exception(node):
                    snippet = self._get_snippet(source_lines, node.lineno)
                    issues.append(self._create_issue(
                        line=node.lineno,
                        col=node.col_offset,
                        snippet=snippet
                    ))

        return issues

    def _is_swallowing_exception(self, handler: ast.ExceptHandler) -> bool:
        """Check if this exception handler is swallowing exceptions"""
        # Check if it's a broad exception type
        if not self._is_broad_exception(handler):
            return False

        # Check if body just swallows (pass, ellipsis, or only logging)
        return self._is_swallowing_body(handler.body)

    def _is_broad_exception(self, handler: ast.ExceptHandler) -> bool:
        """Check if exception type is overly broad"""
        # Bare except
        if handler.type is None:
            return True

        # except Exception or except BaseException
        if isinstance(handler.type, ast.Name):
            return handler.type.id in ("Exception", "BaseException")

        # Handle tuple of exceptions: except (Exception, SomeOther)
        if isinstance(handler.type, ast.Tuple):
            for elt in handler.type.elts:
                if isinstance(elt, ast.Name) and elt.id in ("Exception", "BaseException"):
                    return True

        return False

    def _is_swallowing_body(self, body: list[ast.stmt]) -> bool:
        """Check if handler body effectively does nothing"""
        if not body:
            return True

        # Filter out docstrings
        actual_body = []
        for i, stmt in enumerate(body):
            if i == 0 and isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                if isinstance(stmt.value.value, str):
                    continue  # Skip docstring
            actual_body.append(stmt)

        if not actual_body:
            return True

        # Single pass or ellipsis
        if len(actual_body) == 1:
            stmt = actual_body[0]
            if isinstance(stmt, ast.Pass):
                return True
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                if stmt.value.value is ...:
                    return True

        # Only logging without re-raise
        all_logging = True
        has_raise = False

        for stmt in actual_body:
            if isinstance(stmt, ast.Raise):
                has_raise = True
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                # Check if it's a logging call
                if not self._is_logging_call(stmt.value):
                    all_logging = False
            else:
                all_logging = False

        # Logging without raise is considered swallowing
        if all_logging and not has_raise and len(actual_body) > 0:
            return True

        return False

    def _is_logging_call(self, call: ast.Call) -> bool:
        """Check if this is a logging/print call"""
        if isinstance(call.func, ast.Attribute):
            # logger.info, logging.warning, etc.
            if call.func.attr in ("debug", "info", "warning", "error", "critical", "exception"):
                return True
        elif isinstance(call.func, ast.Name):
            # print()
            if call.func.id == "print":
                return True
        return False
