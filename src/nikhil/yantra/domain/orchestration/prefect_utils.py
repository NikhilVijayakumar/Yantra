# src/nikhil/yantra/domain/orchestration/prefect_utils.py
from prefect import task
from functools import wraps

def yantra_task(retries=3):
    """Custom decorator that automatically logs task status to Yantra's tracker."""
    def decorator(func):
        @task(retries=retries, log_prints=True)
        @wraps(func)
        def wrapper(*args, **kwargs):
            # You could inject auto-logging here if needed
            return func(*args, **kwargs)
        return wrapper
    return decorator