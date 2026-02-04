"""Shared test fixtures for CodeSentry"""

import ast
from pathlib import Path

import pytest

from codesentry.analyzer import AnalysisEngine
from codesentry.patterns import ALL_PATTERNS


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def engine():
    """Analysis engine with all patterns loaded."""
    return AnalysisEngine(ALL_PATTERNS)


@pytest.fixture
def analyze(engine):
    """Helper that analyzes a fixture file by name."""
    def _analyze(fixture_name: str):
        path = FIXTURES_DIR / fixture_name
        assert path.exists(), f"Fixture not found: {path}"
        return engine.analyze_file(path)
    return _analyze


@pytest.fixture
def analyze_source(engine):
    """Helper that analyzes a source string."""
    def _analyze(source: str):
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(source)
            f.flush()
            return engine.analyze_file(Path(f.name))
    return _analyze
