# Orchestration Module - Architecture

## Figure 1: Class Diagram — Orchestration Components

*Caption: Class diagram showing the `YantraContext` singleton, the `yantra_task` decorator factory, and the dependency on `IExperimentTracker` from the Observability module. This module is the only one in Yantra with a cross-module dependency. All class and method names verified against source code.*

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

*Caption: Component-level view showing how the Orchestration module bridges the Observability module (via `IExperimentTracker`) with the Prefect SDK. This is the only cross-module dependency in the Yantra system. Verified via `import` statements across all source files.*

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
        FN["functools.wraps"]
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
    DEC -->|preserves metadata via| FN
    DEC -->|creates spans via| PROTO
    MLF -->|implements| PROTO
    APP -->|decorates functions with| DEC
    APP -->|initializes| CTX
```

---

## Figure 4: State Diagram — Decorated Task Lifecycle

*Caption: State machine showing all possible states of a `@yantra_task`-decorated function during execution, including the graceful degradation path and retry cycle.*

```mermaid
stateDiagram-v2
    [*] --> PrefectScheduled
    PrefectScheduled --> TrackerLookup : Prefect invokes wrapper
    TrackerLookup --> Degraded : tracker = None
    TrackerLookup --> BindingArgs : tracker exists
    Degraded --> DirectExecution : logger.warning()
    DirectExecution --> [*] : return result
    BindingArgs --> SpanCreated : inspect.signature().bind()
    SpanCreated --> Executing : with tracker.start_span()
    Executing --> SpanSuccess : result obtained
    Executing --> SpanError : exception raised
    SpanSuccess --> [*] : set_outputs + "success"
    SpanError --> PrefectRetry : set_attribute("error") + re-raise
    PrefectRetry --> TrackerLookup : retry attempt (up to r times)
    PrefectRetry --> [*] : max retries exhausted
```

---

## Figure 5: Decorator Composition Stack

*Caption: Visual representation of the 3-layer decorator stack showing how `@yantra_task` composes Prefect task wrapping, MLflow span wrapping, and `functools.wraps` metadata preservation.*

```mermaid
flowchart TB
    subgraph "Layer 1: Prefect Task (outermost)"
        P_TASK["prefect.task()\nRetries, scheduling, DAG\nConcurrency management"]
    end

    subgraph "Layer 2: functools.wraps (metadata)"
        F_WRAPS["functools.wraps(func)\nPreserve __name__, __doc__\nPreserve __module__"]
    end

    subgraph "Layer 3: MLflow Span (instrumentation)"
        M_SPAN["tracker.start_span()\nInput capture, output truncation\nError attribute setting"]
    end

    subgraph "Layer 4: Original Function (innermost)"
        FUNC["func(*args, **kwargs)\nBusiness logic\nRaises exceptions naturally"]
    end

    P_TASK --> F_WRAPS
    F_WRAPS --> M_SPAN
    M_SPAN --> FUNC

    style P_TASK fill:#2d6a4f,color:#fff
    style F_WRAPS fill:#40916c,color:#fff
    style M_SPAN fill:#52b788,color:#000
    style FUNC fill:#95d5b2,color:#000
```

---

## Figure 6: Data Flow Diagram — Information Captured per Task Run

*Caption: Shows what data flows through the decorator during each task execution, from raw function arguments to structured span attributes.*

```mermaid
flowchart LR
    subgraph "Input Sources"
        ARGS["Positional Args\n(*args)"]
        KW["Keyword Args\n(**kwargs)"]
        FNAME["Function Name\n(func.__name__)"]
    end

    subgraph "Processing"
        BIND["inspect.signature()\n.bind().arguments"]
        TRUNC["str(result)[:1000]"]
        ERR["str(exception)"]
    end

    subgraph "MLflow Span Attributes"
        S_IN["span.inputs\n(bound args dict)"]
        S_OUT["span.outputs\n(truncated result)"]
        S_STATUS["span.status\n('success'/'error')"]
        S_ERR["span.error.message\n(exception text)"]
        S_NAME["span.name\n(task name)"]
    end

    subgraph "Prefect Attributes"
        P_LOG["Task logs\n(via get_run_logger)"]
        P_RETRY["Retry metadata\n(attempt count)"]
    end

    ARGS --> BIND
    KW --> BIND
    BIND --> S_IN
    FNAME --> S_NAME
    TRUNC --> S_OUT
    ERR --> S_ERR
    S_STATUS --> P_LOG
    S_ERR --> P_LOG
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

---

## Table 3: Cross-Module Dependency Analysis

*Caption: The orchestration module's dependency on observability is the only inter-module dependency in Yantra, making it the system's integration point.*

| S.No | Import | From Module | Used In | Purpose |
|:---:|:---|:---|:---|:---|
| 1 | `IExperimentTracker` | `observability` | `context.py:L4` | Type annotation for tracker |
| 2 | `YantraContext` | `orchestration.context` | `prefect_utils.py:L6` | Tracker lookup |
| 3 | `task`, `get_run_logger` | `prefect` (external) | `prefect_utils.py:L4` | Workflow engine |
| 4 | `inspect` | stdlib | `prefect_utils.py:L3` | Argument binding |
| 5 | `functools` | stdlib | `prefect_utils.py:L2` | Metadata preservation |

---

## Table 4: Error Handling Strategy

*Caption: How errors are handled at each layer of the decorated function.*

| S.No | Error Source | Detection | Span Action | Prefect Action | Source |
|:---:|:---|:---|:---|:---|:---|
| 1 | Function exception | `except Exception as e` | Set "error" + message | Re-raise for retry | `prefect_utils.py:L61-L66` |
| 2 | Missing tracker | `if not tracker` | No span created | Standard execution | `prefect_utils.py:L43-L45` |
| 3 | Signature binding failure | `inspect.signature().bind()` | Not caught | `TypeError` propagated | `prefect_utils.py:L36` |

---

## Table 5: Architectural Design Decisions

*Caption: Key design decisions in the orchestration module with rationale and trade-offs.*

| S.No | Decision | Rationale | Alternative | Trade-off |
|:---:|:---|:---|:---|:---|
| 1 | Decorator factory pattern | Configurable retry/name params | Simple decorator | Flexibility vs. complexity |
| 2 | Class-level singleton context | Global DI without instance management | `contextvars.ContextVar` | Simplicity vs. thread safety |
| 3 | `@functools.wraps` inside `@task` | Preserve original function metadata | Omit wraps | Debuggability vs. none |
| 4 | Output truncation at 1000 chars | Prevent large spans | Configurable limit | Predictability vs. flexibility |
| 5 | Re-raise exception after logging | Preserve Prefect retry semantics | Swallow exception | Correctness vs. none |
| 6 | Bind args before tracker check | Always capture inputs | Lazy bind | Consistency vs. minor overhead |
| 7 | `YantraContext` not in `__init__.py` | Implementation detail exposure | Export it | Encapsulation vs. usability |
