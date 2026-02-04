"""Tests for CS004 — Hardcoded Secrets."""

import pytest


class TestCS004HardcodedSecrets:
    """CS004 detects API keys, passwords, tokens hardcoded in source."""

    def test_detects_hardcoded_secrets(self, analyze):
        result = analyze("test_cs004_secrets.py")
        cs004 = [i for i in result.issues if i.pattern_id == "CS004"]
        assert len(cs004) >= 2, f"Expected at least 2 CS004 hits, got {len(cs004)}"

    def test_ignores_env_vars(self, analyze):
        """os.environ.get() and os.environ[] are safe."""
        result = analyze("test_cs004_secrets.py")
        cs004 = [i for i in result.issues if i.pattern_id == "CS004"]
        for issue in cs004:
            assert "os.environ" not in issue.snippet

    def test_ignores_placeholder_values(self, analyze):
        result = analyze("test_cs004_secrets.py")
        cs004 = [i for i in result.issues if i.pattern_id == "CS004"]
        for issue in cs004:
            assert "your-api-key-here" not in issue.snippet

    def test_severity_is_critical(self, analyze):
        result = analyze("test_cs004_secrets.py")
        cs004 = [i for i in result.issues if i.pattern_id == "CS004"]
        for issue in cs004:
            assert issue.severity.name == "CRITICAL"

    def test_max_severity_code_is_3(self, analyze):
        result = analyze("test_cs004_secrets.py")
        assert result.max_severity_code == 3
