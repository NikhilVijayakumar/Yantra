# Orchestration Module - Test Strategy

## Unit Test Scenarios
-   **[ORCH-UT-001] Context Management:** Verify `set_tracker` and `get_tracker` behave as expected.
-   **[ORCH-UT-002] Decorator Passthrough:** Verify `@yantra_task` correctly registers a Prefect task (name, retries).
-   **[ORCH-UT-003] Wrapper Logic:** 
    -   Mock `YantraContext.get_tracker()`.
    -   Call the decorated function.
    -   Verify `tracker.start_span` is called.
    -   Verify inputs/outputs are logged.

## E2E Test Scenarios
-   **[ORCH-E2E-001] Full Flow with Tracking:**
    -   Setup real `MLflowTracker`.
    -   Run a simple Prefect flow with `@yantra_task`.
    -   Verify in MLflow UI that the Trace exists and contains spans for the tasks.
-   **[ORCH-E2E-002] Error Handling:**
    -   Create a task that raises an exception.
    -   Verify the exception is re-raised (Prefect handles retry).
    -   Verify the trace span is marked as `status=error`.
