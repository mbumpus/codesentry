# Test file for CS004 - Hardcoded Secrets
# NOTE: These are FAKE patterns designed to trigger detection without triggering GitHub secret scanning

# Direct hardcoded secrets - CS004 should trigger
API_KEY = "sk-FAKE_KEY_FOR_TESTING_01234567890abcdefghijk"  # CS004 - OpenAI key pattern
DATABASE_URL = "postgresql://admin:supersecret@prod-db.example.com/myapp"  # CS004 - URL with credentials
SLACK_TOKEN = "xoxb-fake-token-for-testing-purposes-only"  # CS004 - Slack-like token
AWS_ACCESS_KEY_ID = "AKIAFAKEKEY12345678"  # CS004 - AWS key pattern
PRIVATE_KEY = "-----BEGIN RSA PRIVATE KEY-----\nFAKE_KEY_DATA\n-----END RSA PRIVATE KEY-----"  # CS004

# Safe patterns - should NOT trigger
import os
SAFE_KEY = os.environ.get("API_KEY")  # OK - from environment
SAFE_DATABASE = os.environ["DATABASE_URL"]  # OK - from environment

# Placeholder values - should NOT trigger
EXAMPLE_KEY = "your-api-key-here"  # OK - placeholder
TEST_TOKEN = "test-token-12345"  # OK - test value
FAKE_SECRET = "fake-secret-for-testing"  # OK - obviously fake

# Short values - should NOT trigger
SHORT = "abc123"  # OK - too short to be a real secret
