# Test file with no issues - should pass clean

import os
from typing import Optional, List


def fetch_user(user_id: int) -> Optional[dict]:
    """Fetch user by ID with proper error handling."""
    try:
        return database.get_user(user_id)
    except UserNotFoundError:
        return None
    except DatabaseConnectionError as e:
        logger.error(f"Database error: {e}")
        raise


def process_items(items: Optional[List[str]] = None) -> List[str]:
    """Process items with correct mutable default handling."""
    if items is None:
        items = []
    return [item.upper() for item in items]


async def fetch_data_async(url: str) -> dict:
    """Async function using proper async libraries."""
    import asyncio
    
    await asyncio.sleep(0.1)  # Correct: async sleep
    # In real code, would use aiohttp here
    return {"status": "ok"}


# Correct way to handle secrets
API_KEY = os.environ.get("API_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///local.db")


def calculate_tax(amount: float, region: str) -> float:
    """Calculate tax - fully implemented, no TODOs."""
    tax_rates = {
        "US": 0.08,
        "UK": 0.20,
        "DE": 0.19,
    }
    if region not in tax_rates:
        raise ValueError(f"Unknown region: {region}")
    return amount * tax_rates[region]
