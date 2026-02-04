"""Test that clean code produces no issues."""


def test_clean_file_has_no_issues(analyze):
    result = analyze("clean_file.py")
    assert result.total_issues == 0
    assert result.parse_error is None
    assert result.max_severity_code == 0
