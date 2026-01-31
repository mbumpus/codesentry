# Test file for CS001 - Generic Exception Swallow


def bad_fetch():
    try:
        data = fetch_remote()
    except Exception:
        pass  # CS001 should trigger


def also_bad():
    try:
        process()
    except:  # Bare except - CS001
        pass


def bad_with_logging():
    try:
        something()
    except Exception as e:
        print(e)  # CS001 - just logging without re-raise


def acceptable_specific():
    try:
        optional_cleanup()
    except FileNotFoundError:  # Specific - OK
        pass


def acceptable_reraise():
    try:
        risky_op()
    except Exception as e:
        logger.error(f"Failed: {e}")
        raise  # Re-raises - OK


def acceptable_handling():
    try:
        connect()
    except ConnectionError:
        return fallback_connection()
