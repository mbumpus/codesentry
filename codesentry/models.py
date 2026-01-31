"""Data models for CodeSentry"""

from dataclasses import dataclass, field
from enum import IntEnum
from typing import List, Optional


class Severity(IntEnum):
    """Issue severity levels mapped to exit codes"""
    WARNING = 1
    ERROR = 2
    CRITICAL = 3


@dataclass
class Location:
    """Source code location"""
    line: int
    col: int
    end_line: Optional[int] = None
    end_col: Optional[int] = None


@dataclass
class TeachingInfo:
    """Educational content for a pattern"""
    what: str
    why: str
    fix: str
    spot_it_yourself: str
    example_bad: str
    example_good: str


@dataclass
class Issue:
    """A detected issue in the code"""
    pattern_id: str
    pattern_name: str
    category: str
    severity: Severity
    location: Location
    snippet: str
    teaching: TeachingInfo


@dataclass
class AnalysisResult:
    """Result of analyzing a file"""
    file_path: str
    issues: List[Issue] = field(default_factory=list)
    parse_error: Optional[str] = None
    
    @property
    def total_issues(self) -> int:
        return len(self.issues)
    
    @property
    def by_severity(self) -> dict:
        counts = {"critical": 0, "error": 0, "warning": 0}
        for issue in self.issues:
            if issue.severity == Severity.CRITICAL:
                counts["critical"] += 1
            elif issue.severity == Severity.ERROR:
                counts["error"] += 1
            else:
                counts["warning"] += 1
        return counts
    
    @property
    def max_severity_code(self) -> int:
        """Return exit code based on highest severity found"""
        if not self.issues:
            return 0
        return max(issue.severity.value for issue in self.issues)
