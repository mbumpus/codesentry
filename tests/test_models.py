"""Tests for data models."""

from codesentry.models import AnalysisResult, Issue, Location, Severity, TeachingInfo


class TestSeverity:
    def test_ordering(self):
        assert Severity.WARNING < Severity.ERROR < Severity.CRITICAL

    def test_values(self):
        assert Severity.WARNING == 1
        assert Severity.ERROR == 2
        assert Severity.CRITICAL == 3


class TestAnalysisResult:
    def test_empty_result(self):
        result = AnalysisResult(file_path="test.py")
        assert result.total_issues == 0
        assert result.max_severity_code == 0
        assert result.parse_error is None

    def test_severity_counts(self):
        teaching = TeachingInfo(
            what="test", why="test", fix="test",
            spot_it_yourself="test", example_bad="bad", example_good="good"
        )
        result = AnalysisResult(file_path="test.py", issues=[
            Issue("CS001", "test", "cat", Severity.WARNING,
                  Location(1, 0), "snippet", teaching),
            Issue("CS004", "test", "cat", Severity.CRITICAL,
                  Location(2, 0), "snippet", teaching),
        ])
        assert result.total_issues == 2
        assert result.by_severity["warning"] == 1
        assert result.by_severity["critical"] == 1
        assert result.max_severity_code == 3

    def test_parse_error(self):
        result = AnalysisResult(file_path="bad.py", parse_error="Syntax error")
        assert result.parse_error == "Syntax error"
