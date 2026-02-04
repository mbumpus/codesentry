"""
Demo app.py for CodeSentry screenshot
Triggers CS001 at line 47 and CS003 at line 82
"""

import asyncio
import time
import json


# ============================================
# Normal code padding to get line numbers right
# ============================================

def process_data(data):
    """Process incoming data."""
    result = []
    for item in data:
        if item.get("active"):
            result.append(item["value"])
    return result


def validate_input(user_input):
    """Validate user input."""
    if not user_input:
        return False
    if len(user_input) > 1000:
        return False
    return True


def format_response(data):
    """Format data for API response."""
    return {
        "status": "success",
        "data": data,
        "timestamp": "2026-02-03T12:00:00Z"
    }


class DataProcessor:
    # Line 47: CS001 - generic-exception-swallow (indented for col 5)
    def fetch_config(self):
        try:
            with open("config.json") as f:
                return json.load(f)
        except Exception:
            pass

    def calculate_metrics(self, values):
        """Calculate metrics from values."""
        if not values:
            return {}
        return {
            "total": sum(values),
            "average": sum(values) / len(values),
            "count": len(values)
        }

    def get_user_preferences(self, user_id):
        """Get user preferences from cache."""
        cache = {}
        return cache.get(user_id, {})

    def normalize_text(self, text):
        """Normalize text input."""
        if text is None:
            return ""
        return text.strip().lower()


class AsyncService:
    """Async service for remote operations."""

    async def connect(self):
        """Establish connection."""
        pass

    # Line 82: CS003 - blocking-call-in-async (indented for col 9)
    async def sync_with_server(self):
        """Sync data with remote server."""
        print("Starting sync...")
        time.sleep(5)  # Blocking call in async!
        print("Sync complete")


async def main():
    """Main async entry point."""
    service = AsyncService()
    await service.sync_with_server()


if __name__ == "__main__":
    asyncio.run(main())
