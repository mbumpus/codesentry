"""Output formatting and reporting for CodeSentry"""

import json
import sys
from datetime import datetime, timezone
from typing import TextIO

from . import __version__
from .models import AnalysisResult, Issue, Severity


# ANSI color codes
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    DIM = "\033[2m"


def _supports_color(stream: TextIO) -> bool:
    """Check if the stream supports ANSI colors"""
    if not hasattr(stream, 'isatty'):
        return False
    if not stream.isatty():
        return False
    return True


class Reporter:
    """Format and output analysis results"""
    
    SEVERITY_ICONS = {
        Severity.WARNING: "⚠️ ",
        Severity.ERROR: "❌",
        Severity.CRITICAL: "🚨",
    }
    
    SEVERITY_CODES = {
        Severity.WARNING: "W",
        Severity.ERROR: "E",
        Severity.CRITICAL: "C",
    }
    
    def __init__(self, format: str = "text", mode: str = "default", 
                 color: bool = True, stream: TextIO = None):
        """
        Initialize reporter.
        
        Args:
            format: Output format ('text' or 'json')
            mode: Text mode ('default', 'teach', or 'quick')
            color: Enable colored output
            stream: Output stream (defaults to stdout)
        """
        self.format = format
        self.mode = mode
        self.stream = stream or sys.stdout
        self.color = color and _supports_color(self.stream)
    
    def report(self, result: AnalysisResult) -> None:
        """Output the analysis result"""
        if result.parse_error:
            self._print_error(f"Parse error: {result.parse_error}")
            return
        
        if self.format == "json":
            self._report_json(result)
        else:
            self._report_text(result)
    
    def _report_json(self, result: AnalysisResult) -> None:
        """Output result as JSON"""
        output = {
            "file": result.file_path,
            "scan_time": datetime.now(timezone.utc).isoformat(),
            "version": __version__,
            "summary": {
                "total_issues": result.total_issues,
                "by_severity": result.by_severity,
            },
            "issues": [
                {
                    "id": issue.pattern_id,
                    "name": issue.pattern_name,
                    "category": issue.category,
                    "severity": issue.severity.name.lower(),
                    "location": {
                        "line": issue.location.line,
                        "col": issue.location.col,
                        "end_line": issue.location.end_line,
                        "end_col": issue.location.end_col,
                    },
                    "snippet": issue.snippet,
                    "teaching": {
                        "what": issue.teaching.what,
                        "why": issue.teaching.why,
                        "fix": issue.teaching.fix,
                        "spot_it_yourself": issue.teaching.spot_it_yourself,
                    },
                }
                for issue in result.issues
            ],
        }
        self.stream.write(json.dumps(output, indent=2) + "\n")
    
    def _report_text(self, result: AnalysisResult) -> None:
        """Output result as formatted text"""
        if not result.issues:
            self._print_success(f"✅ No issues found in {result.file_path}")
            return
        
        # Header
        self._print_header(result)
        
        # Issues
        if self.mode == "teach":
            # Group by pattern ID for teach mode
            self._print_grouped_issues_teach(result)
        else:
            for issue in result.issues:
                if self.mode == "quick":
                    self._print_issue_quick(issue, result.file_path)
                else:
                    self._print_issue_default(issue, result.file_path)
        
        # Summary
        if self.mode != "quick":
            self._print_summary(result)
    
    def _print_grouped_issues_teach(self, result: AnalysisResult) -> None:
        """Print issues grouped by pattern with teaching shown once per pattern"""
        from collections import defaultdict
        
        # Group issues by pattern_id
        grouped = defaultdict(list)
        for issue in result.issues:
            grouped[issue.pattern_id].append(issue)
        
        for pattern_id, issues in grouped.items():
            # Use first issue for teaching content (same for all)
            first = issues[0]
            count = len(issues)
            severity_color = self._get_severity_color(first.severity)
            
            self._print(self._colorize("═" * 60, Colors.BOLD))
            self._print(self._colorize(
                f"🔍 {first.pattern_name} ({pattern_id}) — {count} occurrence{'s' if count > 1 else ''}", 
                severity_color + Colors.BOLD
            ))
            self._print(f"   Severity: {first.severity.name.lower()} | Category: {first.category}")
            self._print(self._colorize("─" * 60, Colors.DIM))
            
            # List all locations with snippets
            self._print(self._colorize("\n📍 LOCATIONS:", Colors.BOLD))
            for issue in issues:
                loc = f"{result.file_path}:{issue.location.line}:{issue.location.col}"
                snippet = issue.snippet.strip()[:60] if issue.snippet else ""
                if snippet:
                    self._print(f"   • {loc}")
                    self._print(self._colorize(f"     {snippet}", Colors.DIM))
                else:
                    self._print(f"   • {loc}")
            
            self._print(self._colorize("\n❓ WHY IT MATTERS:", Colors.BOLD))
            for line in self._wrap_text(first.teaching.why, 55):
                self._print(f"   {line}")
            
            self._print(self._colorize("\n✅ HOW TO FIX:", Colors.BOLD))
            for line in self._wrap_text(first.teaching.fix, 55):
                self._print(f"   {line}")
            
            self._print(self._colorize("\n📝 CODE EXAMPLE:", Colors.BOLD))
            self._print(self._colorize("   ❌ Bad:", Colors.RED))
            for line in first.teaching.example_bad.split("\n"):
                self._print(self._colorize(f"      {line}", Colors.DIM))
            
            self._print(self._colorize("\n   ✅ Good:", Colors.GREEN))
            for line in first.teaching.example_good.split("\n"):
                self._print(self._colorize(f"      {line}", Colors.DIM))
            
            self._print(self._colorize("\n🎓 SPOT IT YOURSELF:", Colors.BOLD))
            for line in self._wrap_text(first.teaching.spot_it_yourself, 55):
                self._print(f"   {line}")
            
            self._print(self._colorize("\n" + "═" * 60, Colors.BOLD))
            self._print("")
    
    def _print_header(self, result: AnalysisResult) -> None:
        """Print analysis header"""
        if self.mode == "quick":
            return
        
        self._print("")
        self._print(self._colorize(f"CodeSentry v{__version__}", Colors.BOLD))
        self._print(self._colorize(f"Scanning: {result.file_path}", Colors.DIM))
        self._print("")
    
    def _print_issue_quick(self, issue: Issue, file_path: str) -> None:
        """Print minimal lint-style output"""
        severity_code = self.SEVERITY_CODES[issue.severity]
        line = f"{file_path}:{issue.location.line}:{issue.location.col}: {severity_code} {issue.pattern_id} {issue.pattern_name}"
        self._print(line)
    
    def _print_issue_default(self, issue: Issue, file_path: str) -> None:
        """Print balanced output with brief explanation"""
        icon = self.SEVERITY_ICONS[issue.severity]
        severity_color = self._get_severity_color(issue.severity)
        
        self._print(self._colorize(f"╭─ {icon} {issue.pattern_name} ({issue.pattern_id})", severity_color))
        self._print(self._colorize(f"│  {file_path}:{issue.location.line}:{issue.location.col}", Colors.DIM))
        self._print("│")
        self._print(f"│  {issue.teaching.what}")
        self._print("│")
        self._print(self._colorize(f"│  💡 {issue.teaching.fix}", Colors.GREEN))
        self._print("╰" + "─" * 50)
        self._print("")
    
    def _print_issue_teach(self, issue: Issue, file_path: str) -> None:
        """Print full educational output"""
        icon = self.SEVERITY_ICONS[issue.severity]
        severity_color = self._get_severity_color(issue.severity)
        
        self._print(self._colorize("═" * 60, Colors.BOLD))
        self._print(self._colorize(f"🔍 ISSUE: {issue.pattern_name} ({issue.pattern_id})", severity_color + Colors.BOLD))
        self._print(f"   Severity: {issue.severity.name.lower()} | Category: {issue.category}")
        self._print(f"   Location: {file_path}:{issue.location.line}:{issue.location.col}")
        self._print(self._colorize("─" * 60, Colors.DIM))
        
        self._print(self._colorize("\n📍 WHAT'S HAPPENING:", Colors.BOLD))
        self._print(f"   {issue.teaching.what}")
        
        self._print(self._colorize("\n❓ WHY IT MATTERS:", Colors.BOLD))
        for line in self._wrap_text(issue.teaching.why, 55):
            self._print(f"   {line}")
        
        self._print(self._colorize("\n✅ HOW TO FIX:", Colors.BOLD))
        for line in self._wrap_text(issue.teaching.fix, 55):
            self._print(f"   {line}")
        
        self._print(self._colorize("\n📝 CODE EXAMPLE:", Colors.BOLD))
        self._print(self._colorize("   ❌ Bad:", Colors.RED))
        for line in issue.teaching.example_bad.split("\n"):
            self._print(self._colorize(f"      {line}", Colors.DIM))
        
        self._print(self._colorize("\n   ✅ Good:", Colors.GREEN))
        for line in issue.teaching.example_good.split("\n"):
            self._print(self._colorize(f"      {line}", Colors.DIM))
        
        self._print(self._colorize("\n🎓 SPOT IT YOURSELF:", Colors.BOLD))
        for line in self._wrap_text(issue.teaching.spot_it_yourself, 55):
            self._print(f"   {line}")
        
        self._print(self._colorize("\n" + "═" * 60, Colors.BOLD))
        self._print("")
    
    def _print_summary(self, result: AnalysisResult) -> None:
        """Print summary of findings"""
        counts = result.by_severity
        parts = []
        
        if counts["critical"]:
            parts.append(self._colorize(f"{counts['critical']} critical", Colors.RED))
        if counts["error"]:
            parts.append(self._colorize(f"{counts['error']} errors", Colors.YELLOW))
        if counts["warning"]:
            parts.append(self._colorize(f"{counts['warning']} warnings", Colors.CYAN))
        
        summary = ", ".join(parts) if parts else "0 issues"
        self._print(self._colorize("─" * 40, Colors.DIM))
        self._print(f"Found {result.total_issues} issue(s): {summary}")
        self._print("")
    
    def _print(self, text: str) -> None:
        """Print a line to the output stream"""
        self.stream.write(text + "\n")
    
    def _print_error(self, text: str) -> None:
        """Print an error message"""
        self._print(self._colorize(f"Error: {text}", Colors.RED))
    
    def _print_success(self, text: str) -> None:
        """Print a success message"""
        self._print(self._colorize(text, Colors.GREEN))
    
    def _colorize(self, text: str, color: str) -> str:
        """Apply color if enabled"""
        if not self.color:
            return text
        return f"{color}{text}{Colors.RESET}"
    
    def _get_severity_color(self, severity: Severity) -> str:
        """Get color for severity level"""
        return {
            Severity.WARNING: Colors.YELLOW,
            Severity.ERROR: Colors.RED,
            Severity.CRITICAL: Colors.RED + Colors.BOLD,
        }.get(severity, "")
    
    def _wrap_text(self, text: str, width: int) -> list:
        """Simple word-wrap for text"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= width:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(" ".join(current_line))
        
        return lines or [""]
