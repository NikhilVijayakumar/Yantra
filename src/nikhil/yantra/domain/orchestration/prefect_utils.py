# src/nikhil/yantra/domain/orchestration/prefect_utils.py
import functools
import inspect
from prefect import task, get_run_logger

from yantra.domain.orchestration.context import YantraContext


def yantra_task(
        name: str = None,
        retries: int = 3,
        retry_delay_seconds: int = 5,
        log_prints: bool = True
):
    """
    Dual-purpose decorator:
    1. Registers function as a Prefect Task (with retries).
    2. Wraps execution in an MLflow Span (automatic observability).
    """

    def decorator(func):
        # 1. Register with Prefect
        @task(
            name=name or func.__name__,
            retries=retries,
            retry_delay_seconds=retry_delay_seconds,
            log_prints=log_prints
        )
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_run_logger()
            tracker = YantraContext.get_tracker()

            # Capture inputs for logging
            # (binds positional args to variable names)
            func_args = inspect.signature(func).bind(*args, **kwargs)
            func_args.apply_defaults()
            inputs = dict(func_args.arguments)

            task_name = name or func.__name__

            # If no tracker is configured, just run standard Prefect task
            if not tracker:
                logger.warning("⚠️ No Yantra tracker active. Running without MLflow tracing.")
                return func(*args, **kwargs)

            # 2. Wrap in MLflow Span
            # We use the tracker's start_span context manager
            with tracker.start_span(name=task_name, inputs=inputs) as span:
                try:
                    result = func(*args, **kwargs)

                    # Log output to trace
                    # Note: Be careful with huge return objects (DataFrames),
                    # you might want to log metadata (result.shape) instead of raw data.
                    span.set_outputs({"result": str(result)[:1000]})
                    span.set_attribute("status", "success")

                    return result

                except Exception as e:
                    # Log error to trace before crashing
                    span.set_attribute("status", "error")
                    span.set_attribute("error.message", str(e))
                    logger.error(f"❌ Task {task_name} failed: {e}")
                    raise e  # Re-raise so Prefect handles the retry logic

        return wrapper

    return decorator