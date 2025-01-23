from functools import wraps
import time
import traceback

def retry_on_error(max_retries=3):
    """Decorator to retry operations on failure."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        print(f"❌ Failed after {max_retries} attempts: {func.__name__}")
                        raise Exception(f"Error: {str(e)} Trace: {traceback.format_exc()}")
                    print(f"⚠️ Attempt {attempt + 1}/{max_retries} failed, retrying...")
                    time.sleep(2 ** attempt)
            return None
        return wrapper
    return decorator
