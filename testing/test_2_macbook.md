# CodeSentry v0.1.0 — Output Modes Demo

*Real output from scanning `tests/fixtures/test_cs001_exception_swallow.py`*

---

## Teach Mode (`--teach`)

Full educational output — grouped by pattern, all locations listed, one teach block.

```
CodeSentry v0.1.0
Scanning: tests/fixtures/test_cs001_exception_swallow.py

════════════════════════════════════════════════════════════
🔍 generic-exception-swallow (CS001) — 3 occurrences
   Severity: warning | Category: ai-generated-signature
────────────────────────────────────────────────────────────

📍 LOCATIONS:
   • tests/fixtures/test_cs001_exception_swallow.py:7:4
     except Exception:
   • tests/fixtures/test_cs001_exception_swallow.py:14:4
     except:  # Bare except - CS001
   • tests/fixtures/test_cs001_exception_swallow.py:21:4
     except Exception as e:

❓ WHY IT MATTERS:
   This hides bugs, masks crashes, and makes debugging
   nearly impossible. If something fails, you'll never
   know. LLMs often generate this pattern because it
   'prevents errors' in the most superficial way.

✅ HOW TO FIX:
   Catch specific exceptions you can handle. Re-raise or
   log with traceback for unexpected ones.

📝 CODE EXAMPLE:
   ❌ Bad:
      try:
          data = fetch_user(id)
      except Exception:
          pass  # User not found? Network error? Bug? Who knows!

   ✅ Good:
      try:
          data = fetch_user(id)
      except UserNotFoundError:
          return None  # Expected case, handled explicitly
      except NetworkError as e:
          logger.warning(f'Network issue: {e}')
          raise  # Let caller decide retry strategy

🎓 SPOT IT YOURSELF:
   Search for 'except Exception' and 'except:' in your
   codebase. Ask: 'What specific error am I handling
   here?' If you can't answer, you're probably swallowing
   bugs.

════════════════════════════════════════════════════════════

────────────────────────────────────────
Found 3 issue(s): 3 warnings
```

---

## Quick Mode (`--quick`)

Minimal lint-style output for CI/CD pipelines.

```
tests/fixtures/test_cs001_exception_swallow.py:7:4: W CS001 generic-exception-swallow
tests/fixtures/test_cs001_exception_swallow.py:14:4: W CS001 generic-exception-swallow
tests/fixtures/test_cs001_exception_swallow.py:21:4: W CS001 generic-exception-swallow
```

---

## JSON Mode (`--format json`)

Machine-readable output for integrations.

```json
{
  "file": "tests/fixtures/test_cs001_exception_swallow.py",
  "scan_time": "2026-01-31T16:02:40.469564+00:00",
  "version": "0.1.0",
  "summary": {
    "total_issues": 3,
    "by_severity": {
      "critical": 0,
      "error": 0,
      "warning": 3
    }
  },
  "issues": [
    {
      "id": "CS001",
      "name": "generic-exception-swallow",
      "category": "ai-generated-signature",
      "severity": "warning",
      "location": {
        "line": 7,
        "col": 4,
        "end_line": null,
        "end_col": null
      },
      "snippet": "    except Exception:",
      "teaching": {
        "what": "You're catching all exceptions and silently swallowing them.",
        "why": "This hides bugs, masks crashes, and makes debugging nearly impossible. If something fails, you'll never know. LLMs often generate this pattern because it 'prevents errors' in the most superficial way.",
        "fix": "Catch specific exceptions you can handle. Re-raise or log with traceback for unexpected ones.",
        "spot_it_yourself": "Search for 'except Exception' and 'except:' in your codebase. Ask: 'What specific error am I handling here?' If you can't answer, you're probably swallowing bugs."
      }
    },
    {
      "id": "CS001",
      "name": "generic-exception-swallow",
      "category": "ai-generated-signature",
      "severity": "warning",
      "location": {
        "line": 14,
        "col": 4,
        "end_line": null,
        "end_col": null
      },
      "snippet": "    except:  # Bare except - CS001",
      "teaching": {
        "what": "You're catching all exceptions and silently swallowing them.",
        "why": "This hides bugs, masks crashes, and makes debugging nearly impossible. If something fails, you'll never know. LLMs often generate this pattern because it 'prevents errors' in the most superficial way.",
        "fix": "Catch specific exceptions you can handle. Re-raise or log with traceback for unexpected ones.",
        "spot_it_yourself": "Search for 'except Exception' and 'except:' in your codebase. Ask: 'What specific error am I handling here?' If you can't answer, you're probably swallowing bugs."
      }
    },
    {
      "id": "CS001",
      "name": "generic-exception-swallow",
      "category": "ai-generated-signature",
      "severity": "warning",
      "location": {
        "line": 21,
        "col": 4,
        "end_line": null,
        "end_col": null
      },
      "snippet": "    except Exception as e:",
      "teaching": {
        "what": "You're catching all exceptions and silently swallowing them.",
        "why": "This hides bugs, masks crashes, and makes debugging nearly impossible. If something fails, you'll never know. LLMs often generate this pattern because it 'prevents errors' in the most superficial way.",
        "fix": "Catch specific exceptions you can handle. Re-raise or log with traceback for unexpected ones.",
        "spot_it_yourself": "Search for 'except Exception' and 'except:' in your codebase. Ask: 'What specific error am I handling here?' If you can't answer, you're probably swallowing bugs."
      }
    }
  ]
}
```

---

*Same scan, three interfaces. Learn, lint, or integrate.*
