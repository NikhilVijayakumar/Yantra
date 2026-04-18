# Observability Module - Test Strategy

## Unit Test Scenarios
-   **[OBS-UT-001] Tracker Initialization:** Verify `MLflowTracker` initializes with correct URI/experiment.
-   **[OBS-UT-002] Metric Logging:** Mock `mlflow` and verify `log_metric` calls the SDK correctly.
-   **[OBS-UT-003] Protocol Compliance:** Ensure `MLflowTracker` implements all methods of `IExperimentTracker`.
-   **[OBS-UT-004] Arena Execution:** Verify `ModelArena.compare_models` processes DataFrame inputs correctly.

## E2E Test Scenarios
-   **[OBS-E2E-001] Real MLflow Interaction:**
    -   Spin up a local MLflow server (or use mock).
    -   Run a full cycle: `start_run` -> `log_param` -> `log_metric` -> `end_run`.
    -   Verify data exists in the backend.
-   **[OBS-E2E-002] Trace Propagation:**
    -   Simulate a chain of operations using `start_span`.
    -   Verify hierarchy is preserved in logged traces.
