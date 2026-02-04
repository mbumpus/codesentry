"""Tests for CS003 — Blocking Call in Async Function."""

import pytest


class TestCS003AsyncBlocking:
    """CS003 detects blocking calls (time.sleep, requests, open) inside async functions."""

    def test_detects_time_sleep_in_async(self, analyze):
        result = analyze("test_cs003_async_blocking.py")
        cs003 = [i for i in result.issues if i.pattern_id == "CS003"]
        assert any("sleep" in i.snippet for i in cs003), "Should detect time.sleep in async"

    def test_detects_requests_in_async(self, analyze):
        result = analyze("test_cs003_async_blocking.py")
        cs003 = [i for i in result.issues if i.pattern_id == "CS003"]
        assert any("requests" in i.snippet for i in cs003), "Should detect requests.get/post in async"

    def test_detects_open_in_async(self, analyze):
        result = analyze("test_cs003_async_blocking.py")
        cs003 = [i for i in result.issues if i.pattern_id == "CS003"]
        assert any("open" in i.snippet for i in cs003), "Should detect open() in async"

    def test_ignores_regular_functions(self, analyze):
        """Blocking calls in non-async functions are fine."""
        result = analyze("test_cs003_async_blocking.py")
        cs003 = [i for i in result.issues if i.pattern_id == "CS003"]
        for issue in cs003:
            assert "regular_function" not in issue.snippet

    def test_ignores_asyncio_sleep(self, analyze):
        result = analyze("test_cs003_async_blocking.py")
        cs003 = [i for i in result.issues if i.pattern_id == "CS003"]
        for issue in cs003:
            assert "asyncio.sleep" not in issue.snippet

    def test_minimum_detections(self, analyze):
        result = analyze("test_cs003_async_blocking.py")
        cs003 = [i for i in result.issues if i.pattern_id == "CS003"]
        assert len(cs003) >= 3, f"Expected at least 3 CS003 hits, got {len(cs003)}"

    def test_severity_is_error(self, analyze):
        result = analyze("test_cs003_async_blocking.py")
        cs003 = [i for i in result.issues if i.pattern_id == "CS003"]
        for issue in cs003:
            assert issue.severity.name == "ERROR"
