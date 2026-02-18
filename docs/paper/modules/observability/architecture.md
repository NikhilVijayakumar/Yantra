# Observability Module - Architecture

## Figure 1: Class Diagram — Protocol-Based Observability Layer

*Caption: Class hierarchy of the Observability module showing the `IExperimentTracker` protocol, its concrete implementation `MLflowTracker`, and the `ModelArena` evaluation component. All class and method names verified against source code.*

```mermaid
classDiagram
    class IExperimentTracker {
        <<Protocol>>
        +start_run(run_name: str, nested: bool) Any
        +log_metric(key: str, value: float, step: int) None
        +log_param(key: str, value: Any) None
        +log_artifact(local_path: str, artifact_path: str) None
        +log_llm_trace(name: str, inputs: Dict, outputs: Dict, metadata: Dict) None
        +start_span(name: str, inputs: Dict) Any
        +end_run() None
        +autolog_crewai() None
        +autolog_gemini() None
        +enable_system_metrics() None
        +log_dataset(dataset_source: Any, context: str) None
    }

    class MLflowTracker {
        -tracking_uri: str
        -experiment_name: str
        +__init__(tracking_uri: str, experiment_name: str)
        +start_run(run_name: str, nested: bool) Any
        +log_metric(key: str, value: float, step: int) None
        +log_llm_trace(name: str, inputs: Dict, outputs: Dict, metadata: Dict) None
        +start_span(name: str, inputs: Dict) ContextManager
        +enable_system_metrics() None
        +log_dataset(dataset_source: Any, context: str, name: str) None
        +autolog_crewai() None
        +autolog_gemini() None
        +end_run() None
    }

    class ModelArena {
        -tracker_uri: str
        +__init__(tracker_uri: str)
        +compare_models(eval_data: DataFrame, model_uris: List, run_name_prefix: str, prompts_column: str, ground_truth_column: str) DataFrame
    }

    IExperimentTracker <|.. MLflowTracker : implements
    MLflowTracker ..> ModelArena : used alongside

    note for IExperimentTracker "Source: experiment_tracker_protocol.py:L7-L47"
    note for MLflowTracker "Source: mlflow_tracker.py:L11-L92"
    note for ModelArena "Source: arena.py:L9-L70"
```

---

## Figure 2: Sequence Diagram — `log_llm_trace` Adaptive Span Logic

*Caption: Sequence diagram showing the conditional branching in `MLflowTracker.log_llm_trace()`. When a parent span exists, a child span is created; otherwise, a new root trace is started. Verified against `mlflow_tracker.py:L54-L79`.*

```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant MLflowTracker
    participant MLflow as MLflow SDK

    Client->>MLflowTracker: log_llm_trace(name, inputs, outputs, metadata)
    MLflowTracker->>MLflow: get_current_active_span()
    
    alt Active span exists (root_span != None)
        MLflow-->>MLflowTracker: root_span
        MLflowTracker->>MLflow: root_span.set_attributes(metadata)
        MLflowTracker->>MLflow: start_span(name) [child]
        MLflow-->>MLflowTracker: child_span
        MLflowTracker->>MLflow: child_span.set_inputs(inputs)
        MLflowTracker->>MLflow: child_span.set_outputs(outputs)
        MLflowTracker->>MLflow: child_span.set_attributes(metadata)
    else No active span
        MLflow-->>MLflowTracker: None
        MLflowTracker->>MLflow: start_span(name) [new root]
        MLflow-->>MLflowTracker: span
        MLflowTracker->>MLflow: span.set_inputs(inputs)
        MLflowTracker->>MLflow: span.set_outputs(outputs)
        MLflowTracker->>MLflow: span.set_attributes(metadata)
    end

    MLflowTracker-->>Client: Done
```

---

## Figure 3: Component Diagram — Module Dependencies

*Caption: Component-level view showing the Observability module's external and internal dependencies. Verified via `import` statements in source files.*

```mermaid
flowchart TD
    subgraph "Observability Module"
        direction TB
        P["IExperimentTracker\n(Protocol)"]
        T["MLflowTracker\n(Implementation)"]
        A["ModelArena\n(Evaluation)"]
    end

    subgraph "External Dependencies"
        direction TB
        ML["mlflow >= 2.14"]
        PD["pandas"]
        GM["mlflow.metrics.genai"]
    end

    subgraph "Internal Consumers"
        direction TB
        CTX["YantraContext\n(orchestration)"]
        YT["@yantra_task\n(orchestration)"]
    end

    T -->|implements| P
    T -->|wraps| ML
    T -->|uses| PD
    A -->|uses| ML
    A -->|uses| GM
    A -->|uses| PD
    CTX -->|manages| P
    YT -->|calls| T
```

---

## Table 1: Protocol Method Coverage

*Caption: Complete enumeration of `IExperimentTracker` protocol methods and their `MLflowTracker` implementation status. Source: `experiment_tracker_protocol.py:L7-L47`, `mlflow_tracker.py:L11-L92`.*

| S.No | Method | Protocol (L#) | Implementation (L#) | MLflow SDK Call |
|:---:|:---|:---|:---|:---|
| 1 | `start_run` | L10 | L42 | `mlflow.start_run()` |
| 2 | `log_metric` | L12 | L45 | `mlflow.log_metric()` |
| 3 | `log_param` | L14 | L48 | `mlflow.log_param()` |
| 4 | `log_artifact` | L16 | L51 | `mlflow.log_artifact()` |
| 5 | `log_llm_trace` | L18-L24 | L54-L79 | `mlflow.start_span()` |
| 6 | `start_span` | L26-L28 | L81-L89 | `mlflow.start_span()` |
| 7 | `end_run` | L30 | L91 | `mlflow.end_run()` |
| 8 | `autolog_crewai` | L32 | L36 | `mlflow.crewai.autolog()` |
| 9 | `autolog_gemini` | L34 | L39 | `mlflow.gemini.autolog()` |
| 10 | `enable_system_metrics` | L36-L38 | L16-L18 | `mlflow.enable_system_metrics_logging()` |
| 11 | `log_dataset` | L40-L46 | L20-L34 | `mlflow.data.from_pandas()` |
