"""Analysis engine for CodeSentry"""

import ast
from pathlib import Path
from typing import List

from .models import AnalysisResult
from .patterns.base import BasePattern


class AnalysisEngine:
    """Engine that runs all pattern analyzers on source files"""
    
    def __init__(self, patterns: List[BasePattern]):
        """
        Initialize with a list of patterns to check.
        
        Args:
            patterns: List of pattern detector instances
        """
        self.patterns = patterns
    
    def analyze_file(self, file_path: Path) -> AnalysisResult:
        """
        Analyze a Python file for anti-patterns.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            AnalysisResult with all detected issues
        """
        result = AnalysisResult(file_path=str(file_path))
        
        try:
            source = file_path.read_text(encoding='utf-8')
        except Exception as e:
            result.parse_error = f"Failed to read file: {e}"
            return result
        
        source_lines = source.splitlines()
        
        try:
            tree = ast.parse(source, filename=str(file_path))
        except SyntaxError as e:
            result.parse_error = f"Syntax error at line {e.lineno}: {e.msg}"
            return result
        
        # Run all pattern analyzers
        for pattern in self.patterns:
            try:
                issues = pattern.analyze(tree, source_lines, source)
                result.issues.extend(issues)
            except Exception as e:
                # Don't crash on individual pattern failures
                pass
        
        # Sort issues by line number
        result.issues.sort(key=lambda i: (i.location.line, i.location.col))
        
        return result
