# Changelog

All notable changes to CodeSentry will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-31

### Added
- Initial release — Phase 0 MVP
- 5 AST-based pattern detectors:
  - **CS001**: Generic exception swallowing
  - **CS002**: Placeholder code in production (TODO/FIXME with stubs)
  - **CS003**: Blocking calls in async functions
  - **CS004**: Hardcoded secrets
  - **CS005**: Mutable default arguments
- CLI with `scan`, `patterns`, and `version` commands
- Output modes: default, `--teach`, `--quick`, `--format json`
- Exit codes: 0 (clean), 1 (warnings), 2 (errors), 3 (critical)
- Decorator and inheritance-aware detection (reduces false positives)
