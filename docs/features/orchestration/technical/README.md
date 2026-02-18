# Orchestration Module - Technical Documentation

## Design Decisions

### 1. Decorator Pattern (`@yantra_task`)
We use a decorator factory that wraps `prefect.task`. 
-   **Why:** To inject cross-cutting concerns (Observability) transparently.
-   **Mechanism:** 
    1.  Registers the function with Prefect (handling retries/caching).
    2.  Wraps the execution in a wrapper that retrieves the global `tracker`.
    3.  Starts an MLflow Span using the tracker.
    4.  Executes the original function.
    5.  Logs success/failure and returns.

### 2. Singleton Context (`YantraContext`)
We use a class-based singleton to store the `IExperimentTracker` instance.
-   **Why:** Prefect tasks run in separate threads/processes depending on the runner. Passing the `tracker` object to every task explicitly clutters the API signature.
-   **Trade-off:** Global state makes testing slightly harder (need to reset context), but significantly improves developer experience (DX).

## Data Flow

1.  **Flow Start:** User initializes `MLflowTracker` and sets it in `YantraContext`.
2.  **Task Invocation:** Prefect schedules the task.
3.  **Wrapper Execution:** 
    -   `YantraContext.get_tracker()` retrieves the tracker.
    -   If tracker exists, `tracker.start_span()` is called.
    -   Function arguments are bound and logged as `inputs`.
4.  **Task Completion:** 
    -   Result is captured.
    -   Result (truncated) is logged as `outputs`.
    -   Span is closed.

## Contracts

### `yantra_task` Signature
```python
def yantra_task(
    name: str = None,
    retries: int = 3,
    retry_delay_seconds: int = 5,
    log_prints: bool = True
) -> Callable
```

## Dependencies
-   `prefect`: Workflow orchestration engine.
-   `yantra.domain.observability`: For `IExperimentTracker`.
