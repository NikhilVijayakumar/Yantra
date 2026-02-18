# Orchestration Module - Architecture

## Figure 1: Class Diagram — Orchestration Components

*Caption: Class diagram showing the `YantraContext` singleton, the `yantra_task` decorator factory, and the dependency on `IExperimentTracker` from the Observability module. All class and method names verified against source code.*

```mermaid
classDiagram
    class YantraContext {
        -_tracker: Optional~IExperimentTracker~
        +set_tracker(tracker: IExperimentTracker)$ void
        +get_tracker()$ Optional~IExperimentTracker~
    }

    class yantra_task {
        <<decorator factory>>
        +name: str
        +retries: int = 3
        +retry_delay_seconds: int = 5
        +log_prints: bool = True
        +__call__(func) wrapper
    }

    class IExperimentTracker {
        <<Protocol>>
        +start_span(name, inputs) Any
        +log_metric(key, value) None
    }

    class PrefectTask {
        <<external>>
        +name: str
        +retries: int
        +retry_delay_seconds: int
    }

    yantra_task ..> YantraContext : reads tracker from
    yantra_task ..> PrefectTask : wraps function as
    yantra_task ..> IExperimentTracker : creates spans via
    YantraContext o-- IExperimentTracker : holds reference to

    note for YantraContext "Source: context.py:L7-L20"
    note for yantra_task "Source: prefect_utils.py:L9-L70"
```

---

## Figure 2: Sequence Diagram — `@yantra_task` Execution Flow

*Caption: Sequence diagram showing the complete lifecycle of a function decorated with `@yantra_task`. Demonstrates the dual-context wrapping: Prefect task execution with MLflow span creation, argument introspection, and error handling. Verified against `prefect_utils.py:L30-L66`.*

```mermaid
sequenceDiagram
    autonumber
    participant Prefect as Prefect Engine
    participant Wrapper as "@yantra_task wrapper"
    participant Context as YantraContext
    participant Inspect as inspect.signature
    participant Tracker as IExperimentTracker
    participant Func as Original Function

    Prefect->>Wrapper: Execute task (args, kwargs)
    Wrapper->>Prefect: get_run_logger()
    Wrapper->>Context: get_tracker()

    alt Tracker is None
        Context-->>Wrapper: None
        Wrapper->>Wrapper: logger.warning("No tracker")
        Wrapper->>Func: func(*args, **kwargs)
        Func-->>Wrapper: result
        Wrapper-->>Prefect: result
    else Tracker exists
        Context-->>Wrapper: tracker
        Wrapper->>Inspect: signature(func).bind(*args, **kwargs)
        Inspect-->>Wrapper: inputs dict
        Wrapper->>Tracker: start_span(name, inputs)
        Tracker-->>Wrapper: span context

        alt Success
            Wrapper->>Func: func(*args, **kwargs)
            Func-->>Wrapper: result
            Wrapper->>Tracker: span.set_outputs(truncated result)
            Wrapper->>Tracker: span.set_attribute("status", "success")
            Wrapper-->>Prefect: result
        else Exception raised
            Wrapper->>Func: func(*args, **kwargs)
            Func--xWrapper: Exception
            Wrapper->>Tracker: span.set_attribute("status", "error")
            Wrapper->>Tracker: span.set_attribute("error.message", str(e))
            Wrapper--xPrefect: re-raise Exception
            Note over Prefect: Prefect handles retry logic
        end
    end
```

---

## Figure 3: Component Diagram — Module Dependencies and External Integration

*Caption: Component-level view showing how the Orchestration module bridges the Observability module (via `IExperimentTracker`) with the Prefect SDK. Verified via `import` statements across all source files.*

```mermaid
flowchart TD
    subgraph "Orchestration Module"
        direction TB
        CTX["YantraContext\n(Singleton)"]
        DEC["@yantra_task\n(Decorator Factory)"]
    end

    subgraph "Observability Module"
        direction TB
        PROTO["IExperimentTracker\n(Protocol)"]
        MLF["MLflowTracker\n(Implementation)"]
    end

    subgraph "External Dependencies"
        direction TB
        PF["prefect.task"]
        PL["prefect.get_run_logger"]
        INS["inspect.signature"]
    end

    subgraph "Consumer Application"
        direction TB
        APP["User Pipeline Code"]
    end

    CTX -->|holds| PROTO
    DEC -->|reads from| CTX
    DEC -->|wraps as| PF
    DEC -->|uses| PL
    DEC -->|introspects via| INS
    DEC -->|creates spans via| PROTO
    MLF -->|implements| PROTO
    APP -->|decorates functions with| DEC
    APP -->|initializes| CTX
```

---

## Table 1: Decorator Configuration Parameters

*Caption: Parameters accepted by the `@yantra_task` decorator factory, their defaults, and purpose. Source: `prefect_utils.py:L9-L14`.*

| S.No | Parameter | Type | Default | Purpose | Passed To |
|:---:|:---|:---|:---:|:---|:---|
| 1 | `name` | `str` | `None` | Task display name in Prefect UI | `prefect.task(name=)` |
| 2 | `retries` | `int` | 3 | Number of retry attempts on failure | `prefect.task(retries=)` |
| 3 | `retry_delay_seconds` | `int` | 5 | Delay between retries (seconds) | `prefect.task(retry_delay_seconds=)` |
| 4 | `log_prints` | `bool` | `True` | Capture `print()` statements as Prefect logs | `prefect.task(log_prints=)` |

---

## Table 2: Span Attributes Set by Decorator

*Caption: MLflow span attributes automatically set by the `@yantra_task` wrapper during execution. Source: `prefect_utils.py:L49-L66`.*

| S.No | Attribute | Value | Condition | Location |
|:---:|:---|:---|:---|:---|
| 1 | `inputs` | Bound function arguments | Always (when tracker exists) | L49 |
| 2 | `outputs.result` | `str(result)[:1000]` | On success | L56 |
| 3 | `status` | `"success"` | On success | L57 |
| 4 | `status` | `"error"` | On exception | L63 |
| 5 | `error.message` | `str(e)` | On exception | L64 |
