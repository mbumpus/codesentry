"""CS005: Mutable Default Argument Pattern"""

import ast

from ..models import Issue, Severity, TeachingInfo
from .base import BasePattern


class MutableDefaultPattern(BasePattern):
    """Detect mutable default arguments in function definitions"""

    @property
    def id(self) -> str:
        return "CS005"

    @property
    def name(self) -> str:
        return "mutable-default-argument"

    @property
    def category(self) -> str:
        return "python-idiom"

    @property
    def severity(self) -> Severity:
        return Severity.WARNING

    @property
    def description(self) -> str:
        return "Using mutable objects (list, dict, set) as default function arguments"

    def get_teaching(self) -> TeachingInfo:
        return TeachingInfo(
            what="You're using a mutable object (list, dict, set) as a default argument.",
            why="Default arguments are evaluated ONCE when the function is defined, not each time "
                "it's called. This means all calls share the same list/dict/set object. Modifying it "
                "in one call affects all future calls. This is one of Python's most infamous gotchas "
                "and catches everyone at least once.",
            fix="Use None as default and create the mutable object inside the function.",
            spot_it_yourself="In function signatures, look for '=[]', '={}', or '=set()'. These are "
                            "almost always bugs. The pattern 'param=None' followed by "
                            "'if param is None: param = []' is the correct idiom.",
            example_bad="""def add_item(item, items=[]):
    items.append(item)
    return items

add_item('a')  # Returns ['a']
add_item('b')  # Returns ['a', 'b'] - Wait, what?!""",
            example_good="""def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items

add_item('a')  # Returns ['a']
add_item('b')  # Returns ['b'] - Correct!"""
        )

    def analyze(self, tree: ast.AST, source_lines: list[str], source: str) -> list[Issue]:
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                mutable_defaults = self._find_mutable_defaults(node)
                for arg_name, default_node in mutable_defaults:
                    snippet = self._get_snippet(source_lines, node.lineno)
                    issue = self._create_issue(
                        line=default_node.lineno,
                        col=default_node.col_offset,
                        snippet=snippet
                    )
                    # Customize the "what" message with the specific argument
                    issue.teaching = TeachingInfo(
                        what=f"Parameter '{arg_name}' has a mutable default value. "
                             f"This default is shared across all function calls.",
                        why=self.get_teaching().why,
                        fix=f"Change to '{arg_name}=None' and add "
                            f"'if {arg_name} is None: {arg_name} = ...' inside the function.",
                        spot_it_yourself=self.get_teaching().spot_it_yourself,
                        example_bad=self.get_teaching().example_bad,
                        example_good=self.get_teaching().example_good
                    )
                    issues.append(issue)

        return issues

    def _find_mutable_defaults(self, func: ast.FunctionDef) -> list[tuple]:
        """Find arguments with mutable default values"""
        results = []
        args = func.args

        # Check regular positional args with defaults
        # defaults align to the end of args.args
        num_defaults = len(args.defaults)
        num_args = len(args.args)

        for i, default in enumerate(args.defaults):
            if self._is_mutable_default(default):
                arg_index = num_args - num_defaults + i
                arg_name = args.args[arg_index].arg
                results.append((arg_name, default))

        # Check keyword-only args (kw_defaults)
        for i, default in enumerate(args.kw_defaults):
            if default is not None and self._is_mutable_default(default):
                arg_name = args.kwonlyargs[i].arg
                results.append((arg_name, default))

        return results

    def _is_mutable_default(self, node: ast.AST) -> bool:
        """Check if an AST node represents a mutable default value"""
        # Empty list: []
        if isinstance(node, ast.List):
            return True

        # Empty dict: {}
        if isinstance(node, ast.Dict):
            return True

        # Empty set: set() - note: {} is a dict, not a set
        if isinstance(node, ast.Set):
            return True

        # Call to list(), dict(), set()
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in ('list', 'dict', 'set'):
                    return True

        return False
