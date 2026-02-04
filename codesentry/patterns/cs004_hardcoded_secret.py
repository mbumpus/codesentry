"""CS004: Hardcoded Secret Pattern"""

import ast
import re
from typing import Optional

from ..models import Issue, Severity, TeachingInfo
from .base import BasePattern

# Variable name patterns that suggest secrets
SECRET_VAR_PATTERNS = [
    re.compile(r'.*(?:API|ACCESS|SECRET|PRIVATE)[_-]?KEY.*', re.IGNORECASE),
    re.compile(r'.*(?:PASSWORD|PASSWD|PWD).*', re.IGNORECASE),
    re.compile(r'.*(?:TOKEN|AUTH|CREDENTIAL).*', re.IGNORECASE),
    re.compile(r'.*(?:DATABASE|DB)[_-]?(?:URL|URI|CONNECTION).*', re.IGNORECASE),
]

# Value patterns for known secret formats
SECRET_VALUE_PATTERNS = [
    (re.compile(r'sk-[a-zA-Z0-9]{20,}'), "OpenAI API Key"),
    (re.compile(r'ghp_[a-zA-Z0-9]{36}'), "GitHub PAT"),
    (re.compile(r'gho_[a-zA-Z0-9]{36}'), "GitHub OAuth"),
    (re.compile(r'xox[baprs]-[a-zA-Z0-9-]{10,}'), "Slack Token"),
    (re.compile(r'AKIA[0-9A-Z]{16}'), "AWS Access Key"),
    (re.compile(r'sk_live_[a-zA-Z0-9]{24}'), "Stripe Key"),
    (re.compile(r'sk_test_[a-zA-Z0-9]{24}'), "Stripe Test Key"),
]

# URL patterns with embedded credentials
URL_CREDENTIAL_PATTERNS = [
    re.compile(r'://[^:]+:[^@]+@'),  # user:pass@host
]


class HardcodedSecretPattern(BasePattern):
    """Detect hardcoded secrets in source code"""

    @property
    def id(self) -> str:
        return "CS004"

    @property
    def name(self) -> str:
        return "hardcoded-secret"

    @property
    def category(self) -> str:
        return "security"

    @property
    def severity(self) -> Severity:
        return Severity.CRITICAL

    @property
    def description(self) -> str:
        return "API keys, passwords, tokens, or secrets hardcoded in source files"

    def get_teaching(self) -> TeachingInfo:
        return TeachingInfo(
            what="You have a secret (API key, password, token) hardcoded in your source file.",
            why="Secrets in code get committed to git, shared in code reviews, and leaked in logs. "
                "Once a secret is in git history, it's there forever (unless you rewrite history). "
                "Attackers actively scan GitHub for leaked credentials. This is how breaches happen.",
            fix="Use environment variables (os.environ['API_KEY']), a .env file (with python-dotenv), "
                "or a secrets manager. Never commit real credentials.",
            spot_it_yourself="Before every commit, run 'git diff --staged | grep -iE \"key|secret|token|password\"'. "
                            "Better: use pre-commit hooks with tools like detect-secrets or gitleaks.",
            example_bad="""OPENAI_API_KEY = 'sk-abc123def456ghi789jkl012mno345pqr678stu901vwx'
DATABASE_URL = 'postgresql://admin:supersecret123@prod-db.example.com/app'""",
            example_good="""import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
DATABASE_URL = os.environ['DATABASE_URL']"""
        )

    def analyze(self, tree: ast.AST, source_lines: list[str], source: str) -> list[Issue]:
        issues = []

        for node in ast.walk(tree):
            # Check assignments: VAR = 'secret'
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        issue = self._check_assignment(target.id, node.value, source_lines)
                        if issue:
                            issues.append(issue)

            # Check annotated assignments: VAR: str = 'secret'
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name) and node.value:
                    issue = self._check_assignment(node.target.id, node.value, source_lines)
                    if issue:
                        issues.append(issue)

        return issues

    def _check_assignment(self, var_name: str, value_node: ast.AST,
                         source_lines: list[str]) -> Optional[Issue]:
        """Check if an assignment is a hardcoded secret"""

        # Get the string value if it's a constant
        if not isinstance(value_node, ast.Constant):
            return None

        value = value_node.value
        if not isinstance(value, str):
            return None

        # Skip empty strings and very short strings
        if len(value) < 8:
            return None

        # Check if variable name suggests a secret
        is_secret_name = any(pattern.match(var_name) for pattern in SECRET_VAR_PATTERNS)

        # Check if value matches known secret patterns
        secret_type = None
        for pattern, name in SECRET_VALUE_PATTERNS:
            if pattern.search(value):
                secret_type = name
                break

        # Check for URLs with embedded credentials
        has_url_creds = any(pattern.search(value) for pattern in URL_CREDENTIAL_PATTERNS)

        # Determine if this is a secret
        if secret_type or (is_secret_name and self._looks_like_secret(value)) or has_url_creds:
            snippet = self._get_snippet(source_lines, value_node.lineno)
            issue = self._create_issue(
                line=value_node.lineno,
                col=value_node.col_offset,
                snippet=self._redact_snippet(snippet)
            )

            # Customize teaching with specific secret type
            if secret_type:
                issue.teaching = TeachingInfo(
                    what=f"You have a {secret_type} hardcoded in your source file.",
                    why=self.get_teaching().why,
                    fix=self.get_teaching().fix,
                    spot_it_yourself=self.get_teaching().spot_it_yourself,
                    example_bad=self.get_teaching().example_bad,
                    example_good=self.get_teaching().example_good
                )

            return issue

        return None

    def _looks_like_secret(self, value: str) -> bool:
        """Heuristic check if a string looks like a secret"""
        # Skip placeholder values
        placeholders = ('xxx', 'your-', 'example', 'placeholder', 'changeme',
                       'insert', 'replace', '<', '>', 'test', 'fake', 'dummy')
        value_lower = value.lower()
        if any(p in value_lower for p in placeholders):
            return False

        # Skip if it's clearly a path or URL without credentials
        if value.startswith(('/','./','../')):
            return False

        # Skip localhost URLs without credentials
        if 'localhost' in value_lower and '://' in value and '@' not in value:
            return False

        # Check for high entropy (mixed case, numbers, special chars)
        has_upper = any(c.isupper() for c in value)
        has_lower = any(c.islower() for c in value)
        has_digit = any(c.isdigit() for c in value)
        has_special = any(c in '-_' for c in value)

        # A secret typically has mixed character types
        entropy_markers = sum([has_upper, has_lower, has_digit, has_special])

        return len(value) >= 16 and entropy_markers >= 3

    def _redact_snippet(self, snippet: str) -> str:
        """Redact potential secrets in the snippet for safe display"""
        # Redact known patterns
        for pattern, _ in SECRET_VALUE_PATTERNS:
            snippet = pattern.sub('[REDACTED]', snippet)

        # Redact URL credentials
        snippet = re.sub(r'://([^:]+):([^@]+)@', r'://\1:[REDACTED]@', snippet)

        return snippet
