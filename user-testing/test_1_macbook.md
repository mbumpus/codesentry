CodeSentry v0.1.0
Scanning: tests/fixtures/test_cs001_exception_swallow.py

════════════════════════════════════════════════════════════
🔍 ISSUE: generic-exception-swallow (CS001)
   Severity: warning | Category: ai-generated-signature
   Location: tests/fixtures/test_cs001_exception_swallow.py:7:4
────────────────────────────────────────────────────────────

📍 WHAT'S HAPPENING:
   You're catching all exceptions and silently swallowing them.

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

════════════════════════════════════════════════════════════
🔍 ISSUE: generic-exception-swallow (CS001)
   Severity: warning | Category: ai-generated-signature
   Location: tests/fixtures/test_cs001_exception_swallow.py:14:4
────────────────────────────────────────────────────────────

📍 WHAT'S HAPPENING:
   You're catching all exceptions and silently swallowing them.

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

════════════════════════════════════════════════════════════
🔍 ISSUE: generic-exception-swallow (CS001)
   Severity: warning | Category: ai-generated-signature
   Location: tests/fixtures/test_cs001_exception_swallow.py:21:4
────────────────────────────────────────────────────────────

📍 WHAT'S HAPPENING:
   You're catching all exceptions and silently swallowing them.

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
