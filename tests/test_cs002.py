"""Tests for CS002 — Placeholder Code in Production."""

import pytest


class TestCS002PlaceholderCode:
    """CS002 detects TODO/FIXME paired with stubs (pass, ..., NotImplementedError)."""

    def test_detects_todo_with_pass(self, analyze):
        result = analyze("test_cs002_placeholder.py")
        cs002 = [i for i in result.issues if i.pattern_id == "CS002"]
        assert len(cs002) >= 1, "Should detect TODO + pass"

    def test_detects_fixme_with_not_implemented(self, analyze):
        result = analyze("test_cs002_placeholder.py")
        cs002 = [i for i in result.issues if i.pattern_id == "CS002"]
        assert len(cs002) >= 2, "Should detect FIXME + NotImplementedError"

    def test_ignores_implemented_todo(self, analyze):
        """TODO with real code after it is not a placeholder stub."""
        result = analyze("test_cs002_placeholder.py")
        cs002 = [i for i in result.issues if i.pattern_id == "CS002"]
        snippets = " ".join(i.snippet for i in cs002)
        assert "actually_implemented" not in snippets

    def test_severity_is_error(self, analyze):
        result = analyze("test_cs002_placeholder.py")
        cs002 = [i for i in result.issues if i.pattern_id == "CS002"]
        for issue in cs002:
            assert issue.severity.name == "ERROR"


class TestCS002LegitimateStubs:
    """CS002 must NOT flag abstract methods, protocols, or overloads."""

    def test_ignores_abstract_methods(self, analyze):
        result = analyze("test_cs002_legitimate_stubs.py")
        cs002 = [i for i in result.issues if i.pattern_id == "CS002"]
        assert len(cs002) == 0, (
            f"Should not flag abstract/protocol/overload stubs, "
            f"but got {len(cs002)}: {[i.snippet[:60] for i in cs002]}"
        )

    def test_ignores_protocol_stubs(self, analyze):
        result = analyze("test_cs002_legitimate_stubs.py")
        cs002 = [i for i in result.issues if i.pattern_id == "CS002"]
        for issue in cs002:
            assert "Protocol" not in issue.snippet

    def test_ignores_overloads(self, analyze):
        result = analyze("test_cs002_legitimate_stubs.py")
        cs002 = [i for i in result.issues if i.pattern_id == "CS002"]
        for issue in cs002:
            assert "overload" not in issue.snippet
