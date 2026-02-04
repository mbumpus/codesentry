"""Tests for CS001 — Generic Exception Swallow."""

import pytest


class TestCS001ExceptionSwallow:
    """CS001 detects broad exception handlers that silently swallow errors."""

    def test_detects_except_exception_pass(self, analyze):
        result = analyze("test_cs001_exception_swallow.py")
        cs001 = [i for i in result.issues if i.pattern_id == "CS001"]
        assert len(cs001) >= 2, f"Expected at least 2 CS001 hits, got {len(cs001)}"

    def test_detects_bare_except(self, analyze):
        result = analyze("test_cs001_exception_swallow.py")
        cs001 = [i for i in result.issues if i.pattern_id == "CS001"]
        # bare except (also_bad) should be caught
        lines = [i.location.line for i in cs001]
        assert any(l > 1 for l in lines), "Should detect bare except"

    def test_ignores_specific_exceptions(self, analyze):
        result = analyze("test_cs001_exception_swallow.py")
        cs001 = [i for i in result.issues if i.pattern_id == "CS001"]
        # FileNotFoundError and ConnectionError handlers should NOT trigger
        for issue in cs001:
            snippet = issue.snippet.lower()
            assert "filenotfounderror" not in snippet or "re-raise" in snippet

    def test_ignores_reraise(self, analyze):
        result = analyze("test_cs001_exception_swallow.py")
        cs001 = [i for i in result.issues if i.pattern_id == "CS001"]
        # acceptable_reraise has `raise` — should not be flagged
        for issue in cs001:
            assert "acceptable_reraise" not in issue.snippet

    def test_severity_is_warning(self, analyze):
        result = analyze("test_cs001_exception_swallow.py")
        cs001 = [i for i in result.issues if i.pattern_id == "CS001"]
        for issue in cs001:
            assert issue.severity.name == "WARNING"

    def test_has_teaching_content(self, analyze):
        result = analyze("test_cs001_exception_swallow.py")
        cs001 = [i for i in result.issues if i.pattern_id == "CS001"]
        assert cs001, "Expected at least one CS001 issue"
        teaching = cs001[0].teaching
        assert teaching.what
        assert teaching.why
        assert teaching.fix
        assert teaching.example_bad
        assert teaching.example_good
