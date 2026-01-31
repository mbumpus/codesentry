"""Base pattern class for CodeSentry analyzers"""

import ast
from abc import ABC, abstractmethod
from typing import List

from ..models import Issue, Severity, TeachingInfo


class BasePattern(ABC):
    """Abstract base class for pattern detectors"""
    
    @property
    @abstractmethod
    def id(self) -> str:
        """Pattern ID (e.g., CS001)"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Pattern name (e.g., generic-exception-swallow)"""
        pass
    
    @property
    @abstractmethod
    def category(self) -> str:
        """Pattern category (e.g., ai-generated-signature)"""
        pass
    
    @property
    @abstractmethod
    def severity(self) -> Severity:
        """Pattern severity level"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Short description of the pattern"""
        pass
    
    @abstractmethod
    def get_teaching(self) -> TeachingInfo:
        """Return educational content for this pattern"""
        pass
    
    @abstractmethod
    def analyze(self, tree: ast.AST, source_lines: List[str], source: str) -> List[Issue]:
        """
        Analyze AST and source for this pattern.
        
        Args:
            tree: Parsed AST of the source file
            source_lines: Source code split by lines
            source: Full source code string
            
        Returns:
            List of detected issues
        """
        pass
    
    def _get_snippet(self, source_lines: List[str], line: int, context: int = 0) -> str:
        """Extract code snippet around the given line"""
        start = max(0, line - 1 - context)
        end = min(len(source_lines), line + context)
        return "\n".join(source_lines[start:end])
    
    def _create_issue(self, line: int, col: int, snippet: str, 
                      end_line: int = None, end_col: int = None) -> Issue:
        """Helper to create an Issue with this pattern's metadata"""
        from ..models import Location
        return Issue(
            pattern_id=self.id,
            pattern_name=self.name,
            category=self.category,
            severity=self.severity,
            location=Location(line=line, col=col, end_line=end_line, end_col=end_col),
            snippet=snippet,
            teaching=self.get_teaching()
        )
