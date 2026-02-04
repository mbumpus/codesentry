"""Tests for the CLI interface."""

from pathlib import Path

from click.testing import CliRunner

from codesentry.cli import main


FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestCLI:
    """CLI integration tests."""

    def test_version_flag(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "CodeSentry v" in result.output

    def test_version_command(self):
        runner = CliRunner()
        result = runner.invoke(main, ["version"])
        assert result.exit_code == 0
        assert "CodeSentry v" in result.output
        assert "Patterns:" in result.output

    def test_patterns_command(self):
        runner = CliRunner()
        result = runner.invoke(main, ["patterns"])
        assert result.exit_code == 0
        assert "CS001" in result.output
        assert "CS005" in result.output

    def test_scan_clean_file(self):
        runner = CliRunner()
        result = runner.invoke(main, ["scan", str(FIXTURES_DIR / "clean_file.py")])
        assert result.exit_code == 0
        assert "No issues found" in result.output

    def test_scan_with_issues(self):
        runner = CliRunner()
        result = runner.invoke(main, ["scan", str(FIXTURES_DIR / "test_cs005_mutable_default.py")])
        assert result.exit_code > 0  # Should have findings

    def test_scan_quick_mode(self):
        runner = CliRunner()
        result = runner.invoke(main, ["scan", "--quick", str(FIXTURES_DIR / "test_cs005_mutable_default.py")])
        assert result.exit_code > 0
        assert "CS005" in result.output

    def test_scan_json_output(self):
        import json
        runner = CliRunner()
        result = runner.invoke(main, ["scan", "-f", "json", str(FIXTURES_DIR / "test_cs004_secrets.py")])
        data = json.loads(result.output)
        assert "issues" in data
        assert "summary" in data
        assert data["summary"]["total_issues"] > 0

    def test_scan_teach_mode(self):
        runner = CliRunner()
        result = runner.invoke(main, ["scan", "--teach", str(FIXTURES_DIR / "test_cs001_exception_swallow.py")])
        assert "WHY IT MATTERS" in result.output or "HOW TO FIX" in result.output

    def test_scan_teach_and_quick_exclusive(self):
        runner = CliRunner()
        result = runner.invoke(main, ["scan", "--teach", "--quick", str(FIXTURES_DIR / "clean_file.py")])
        assert result.exit_code != 0

    def test_scan_nonexistent_file(self):
        runner = CliRunner()
        result = runner.invoke(main, ["scan", "/nonexistent/file.py"])
        assert result.exit_code != 0

    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "CodeSentry" in result.output
