"""CS003: Blocking Call in Async Function Pattern"""

import ast
from typing import Optional

from ..models import Issue, Severity, TeachingInfo
from .base import BasePattern

# Blocking calls and their async alternatives
BLOCKING_CALLS = {
    # (module, function): async_alternative
    ("time", "sleep"): "asyncio.sleep",
    ("requests", "get"): "aiohttp/httpx",
    ("requests", "post"): "aiohttp/httpx",
    ("requests", "put"): "aiohttp/httpx",
    ("requests", "delete"): "aiohttp/httpx",
    ("requests", "patch"): "aiohttp/httpx",
    ("requests", "head"): "aiohttp/httpx",
    ("requests", "options"): "aiohttp/httpx",
    ("requests", "request"): "aiohttp/httpx",
    ("urllib.request", "urlopen"): "aiohttp/httpx",
}

# Builtin blocking calls
BLOCKING_BUILTINS = {
    "open": "aiofiles.open",
    "input": "aioconsole.ainput",
}


class AsyncBlockingPattern(BasePattern):
    """Detect blocking calls inside async functions"""

    @property
    def id(self) -> str:
        return "CS003"

    @property
    def name(self) -> str:
        return "blocking-call-in-async"

    @property
    def category(self) -> str:
        return "async-concurrency"

    @property
    def severity(self) -> Severity:
        return Severity.ERROR

    @property
    def description(self) -> str:
        return "Using blocking calls inside async functions"

    def get_teaching(self) -> TeachingInfo:
        return TeachingInfo(
            what="You're using a blocking call inside an async function.",
            why="Async functions run on an event loop. Blocking calls freeze the ENTIRE loop, "
                "not just your function. If you await asyncio.sleep(1), other tasks run. "
                "If you call time.sleep(1), everything stops for a second. This defeats the "
                "purpose of async and can cause timeouts, unresponsive servers, and cascading failures.",
            fix="Replace blocking calls with their async equivalents: "
                "time.sleep → asyncio.sleep, requests → aiohttp/httpx, open → aiofiles.",
            spot_it_yourself="In any 'async def', search for: time.sleep, requests., open(, input(. "
                            "These are red flags. The rule: if you're in async-land, everything "
                            "I/O-related should be awaited.",
            example_bad="""async def fetch_data(url):
    response = requests.get(url)  # Blocks entire event loop!
    time.sleep(1)  # Even worse - freezes everything
    return response.json()""",
            example_good="""async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            await asyncio.sleep(1)  # Other tasks can run
            return await response.json()"""
        )

    def analyze(self, tree: ast.AST, source_lines: list[str], source: str) -> list[Issue]:
        issues = []

        # Build import alias map
        import_map = self._build_import_map(tree)

        # Find all async functions and check for blocking calls
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                blocking_issues = self._check_async_function(node, source_lines, import_map)
                issues.extend(blocking_issues)

        return issues

    def _build_import_map(self, tree: ast.AST) -> dict:
        """Build mapping of aliases to actual module.function"""
        import_map = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname or alias.name
                    import_map[name] = alias.name
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    name = alias.asname or alias.name
                    import_map[name] = (module, alias.name)

        return import_map

    def _check_async_function(self, func: ast.AsyncFunctionDef,
                              source_lines: list[str], import_map: dict) -> list[Issue]:
        """Check an async function for blocking calls"""
        issues = []

        for node in ast.walk(func):
            if isinstance(node, ast.Call):
                blocking_info = self._is_blocking_call(node, import_map)
                if blocking_info:
                    call_name, alternative = blocking_info
                    snippet = self._get_snippet(source_lines, node.lineno)
                    issue = self._create_issue(
                        line=node.lineno,
                        col=node.col_offset,
                        snippet=snippet
                    )
                    # Add context about which blocking call was found
                    issue.teaching = TeachingInfo(
                        what=f"You're using '{call_name}' (blocking) inside an async function. "
                             f"Use '{alternative}' instead.",
                        why=self.get_teaching().why,
                        fix=f"Replace '{call_name}' with '{alternative}'.",
                        spot_it_yourself=self.get_teaching().spot_it_yourself,
                        example_bad=self.get_teaching().example_bad,
                        example_good=self.get_teaching().example_good
                    )
                    issues.append(issue)

        return issues

    def _is_blocking_call(self, call: ast.Call, import_map: dict) -> Optional[tuple[str, str]]:
        """Check if a call is a known blocking call. Returns (call_name, alternative) or None."""

        # Check for module.function() pattern (e.g., time.sleep())
        if isinstance(call.func, ast.Attribute):
            if isinstance(call.func.value, ast.Name):
                module_alias = call.func.value.id
                func_name = call.func.attr

                # Resolve alias to actual module
                actual_module = import_map.get(module_alias, module_alias)
                if isinstance(actual_module, tuple):
                    # from X import Y as Z - this is direct function access
                    pass
                else:
                    # import X or import X as Y
                    key = (actual_module, func_name)
                    if key in BLOCKING_CALLS:
                        return (f"{module_alias}.{func_name}", BLOCKING_CALLS[key])

        # Check for direct function call (e.g., open(), sleep())
        elif isinstance(call.func, ast.Name):
            func_name = call.func.id

            # Check builtins
            if func_name in BLOCKING_BUILTINS:
                return (func_name, BLOCKING_BUILTINS[func_name])

            # Check if imported from a blocking module
            if func_name in import_map:
                imported_from = import_map[func_name]
                if isinstance(imported_from, tuple):
                    module, actual_func = imported_from
                    key = (module, actual_func)
                    if key in BLOCKING_CALLS:
                        return (func_name, BLOCKING_CALLS[key])

        return None
