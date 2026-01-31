"""Pattern registry for CodeSentry"""

from .base import BasePattern
from .cs001_exception_swallow import ExceptionSwallowPattern
from .cs002_placeholder_code import PlaceholderCodePattern
from .cs003_async_blocking import AsyncBlockingPattern
from .cs004_hardcoded_secret import HardcodedSecretPattern
from .cs005_mutable_default import MutableDefaultPattern

# All available patterns
ALL_PATTERNS: list[BasePattern] = [
    ExceptionSwallowPattern(),
    PlaceholderCodePattern(),
    AsyncBlockingPattern(),
    HardcodedSecretPattern(),
    MutableDefaultPattern(),
]

__all__ = [
    "BasePattern",
    "ALL_PATTERNS",
    "ExceptionSwallowPattern",
    "PlaceholderCodePattern",
    "AsyncBlockingPattern",
    "HardcodedSecretPattern",
    "MutableDefaultPattern",
]
