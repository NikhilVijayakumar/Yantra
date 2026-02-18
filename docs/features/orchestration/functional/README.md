# Orchestration Module - Functional Documentation

## Overview
The **Orchestration** module integrates workflow management (via Prefect) with experiment tracking (via Yantra Observability). It ensures that every step in your pipeline is not only executed robustly with retries but also automatically traced and logged to your experiment tracker.

## Capabilities

### 1. Dual-Purpose Tasks (`@yantra_task`)
-   **Execution Robustness:** Automatically registers functions as Prefect tasks with built-in retry logic (default: 3 retries).
-   **Automatic Tracing:** Wraps every task execution in an MLflow Span.
-   **Input/Output Logging:** Automatically captures function arguments as inputs and return values as outputs in the trace.
-   **Error Capture:** Catches exceptions, logs them to the trace as error events, and re-raises them for Prefect to handle.

### 2. Context Management (`YantraContext`)
-   **Global Tracker Access:** internal mechanism to access the active `ExperimentTracker` without passing it as an argument to every function.
-   **Seamless Integration:** Allows tasks to access the tracker implicitly.

## Usage

### Defining a Task
Replace the standard `@task` decorator with `@yantra_task`:

```python
from yantra.domain.orchestration.prefect_utils import yantra_task

@yantra_task(name="process_data", retries=5)
def process_data(input_path: str):
    # Your logic here
    return {"status": "processed"}
```

### Running a Pipeline
Setup the context before running your flow:
```python
from yantra.domain.orchestration.context import YantraContext
from yantra.domain.observability import MLflowTracker
from prefect import flow

# 1. Setup Tracker
tracker = MLflowTracker(...)
YantraContext.set_tracker(tracker)

# 2. Define Flow
@flow
def main_flow():
    # Calling this will auto-log inputs/outputs to MLflow
    process_data("data.csv")

# 3. Run
main_flow()
```
