# Observability Module - Technical Documentation

## Design Decisions

### 1. Protocol-Based Abstraction
The module uses a `Protocol` (`IExperimentTracker`) to define the contract for experiment tracking.
-   **Why:** This strictly separates the interface from the implementation (`MLflowTracker`).
-   **Benefit:** Enables easy swapping of backends (e.g., replacing MLflow with Weights & Biases) without changing client code. It also facilitates mocking for unit tests.

### 2. MLflow Integration
The current implementation (`MLflowTracker`) wraps the `mlflow` SDK.
-   **v2.14+ Support:** Explicitly supports MLflow Tracing features (`log_llm_trace`, `start_span`) introduced in recent versions.
-   **Autologging:** Provides convenience methods for `crewai` and `gemini` autologging to reduce boilerplate.

### 3. Model Arena (LLM-as-a-Judge)
The `ModelArena` class encapsulates the complexity of `mlflow.evaluate`.
-   **Metric Selection:** Defaults to standard GenAI metrics (Question Answering, Toxicity) but allows for extensibility.
-   **DataFrame Interface:** Uses pandas DataFrames for input/output, aligning with standard Data Science workflows.

## Data Flow

1.  **Client Application** instantiates `MLflowTracker`.
2.  **Tracker** communicates with the MLflow Tracking Server (via HTTP/REST).
3.  **Metrics/Params** are stored in the backend store (SQL DB).
4.  **Artifacts** are uploaded to the artifact store (S3/GCS/Local).
5.  **Traces** are sent to the MLflow Trace backend.

## Contracts

### `IExperimentTracker` Protocol
| Method | Description |
| :--- | :--- |
| `start_run(run_name, nested)` | Starts a new tracking context. |
| `log_metric(key, value, step)` | Logs a numerical value. |
| `log_param(key, value)` | Logs a configuration parameter. |
| `log_llm_trace(name, inputs, ...)` | Logs a structured LLM trace. |
| `enable_system_metrics()` | Starts hardware monitoring. |

## Dependencies
-   `mlflow>=2.14.0`: Core tracking backend.
-   `pandas`: Data structure for evaluation.
-   `crewai` (Optional): For autologging support.
-   `google-generativeai` (Optional): For Gemini autologging.
