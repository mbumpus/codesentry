"""Tests for CS005 — Mutable Default Argument."""

import pytest


class TestCS005MutableDefault:
    """CS005 detects mutable default arguments ([], {}, set(), list(), dict())."""

    def test_detects_list_default(self, analyze):
        result = analyze("test_cs005_mutable_default.py")
        cs005 = [i for i in result.issues if i.pattern_id == "CS005"]
        assert len(cs005) >= 4, f"Expected at least 4 CS005 hits, got {len(cs005)}"

    def test_detects_dict_default(self, analyze):
        result = analyze("test_cs005_mutable_default.py")
        cs005 = [i for i in result.issues if i.pattern_id == "CS005"]
        snippets = " ".join(i.snippet for i in cs005)
        assert "cache" in snippets or "dict" in snippets.lower()

    def test_detects_set_default(self, analyze):
        result = analyze("test_cs005_mutable_default.py")
        cs005 = [i for i in result.issues if i.pattern_id == "CS005"]
        snippets = " ".join(i.snippet for i in cs005)
        assert "set()" in snippets or "seen" in snippets

    def test_ignores_none_pattern(self, analyze):
        result = analyze("test_cs005_mutable_default.py")
        cs005 = [i for i in result.issues if i.pattern_id == "CS005"]
        for issue in cs005:
            assert "good_none_pattern" not in issue.snippet

    def test_ignores_immutable_defaults(self, analyze):
        result = analyze("test_cs005_mutable_default.py")
        cs005 = [i for i in result.issues if i.pattern_id == "CS005"]
        for issue in cs005:
            assert "good_immutable_default" not in issue.snippet
            assert "good_tuple_default" not in issue.snippet
            assert "good_frozenset_default" not in issue.snippet

    def test_severity_is_warning(self, analyze):
        result = analyze("test_cs005_mutable_default.py")
        cs005 = [i for i in result.issues if i.pattern_id == "CS005"]
        for issue in cs005:
            assert issue.severity.name == "WARNING"
