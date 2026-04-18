# Monitoring Module - Architecture

## Figure 1: Class Diagram — Protocol-Based Monitoring Layer

*Caption: Class diagram showing the `IModelMonitor` protocol (runtime-checkable) and its concrete implementation `EvidentlyQualityMonitor`. The protocol enables swapping between Evidently, DeepChecks, or Whylogs without client code changes. All class and method names verified against source code.*

```mermaid
classDiagram
    class IModelMonitor {
        <<Protocol>>
        <<runtime_checkable>>
        +generate_report(df_logs: DataFrame, output_path: str, text_column: str) str
    }

    class EvidentlyQualityMonitor {
        -NLTK_REQUIREMENTS: List~Tuple~
        +__init__() None
        -_download_if_missing(check_path: str, pkg_name: str) None
        -_ensure_nltk_resources() None
        +generate_report(df_logs: DataFrame, output_path: str, text_column: str) str
    }

    class EvidentlyReport {
        <<external>>
        +run(current_data: DataFrame, reference_data: DataFrame) None
        +save_html(path: str) None
    }

    class TextEvals {
        <<external preset>>
    }

    IModelMonitor <|.. EvidentlyQualityMonitor : implements
    EvidentlyQualityMonitor ..> EvidentlyReport : creates and runs
    EvidentlyReport ..> TextEvals : uses preset

    note for IModelMonitor "Source: model_monitor_protocol.py:L7-L28"
    note for EvidentlyQualityMonitor "Source: quality.py:L18-L112"
```

---

## Figure 2: Sequence Diagram — `generate_report` Execution Flow

*Caption: Sequence diagram showing the complete lifecycle of `EvidentlyQualityMonitor.generate_report()`. Demonstrates input validation, NLTK resource check (at init), Evidently report execution, and HTML serialization. Verified against `quality.py:L33-L112`.*

```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant Monitor as EvidentlyQualityMonitor
    participant NLTK as NLTK Data
    participant Evidently as Evidently Report
    participant FS as File System

    Note over Client,Monitor: Constructor (one-time)
    Client->>Monitor: __init__()
    loop For each NLTK resource (4 total)
        Monitor->>NLTK: nltk.data.find(check_path)
        alt Resource exists
            NLTK-->>Monitor: OK (cached)
        else LookupError
            Monitor->>NLTK: nltk.download(pkg_name)
            NLTK-->>Monitor: Downloaded
        end
    end

    Note over Client,Monitor: Report Generation
    Client->>Monitor: generate_report(df_logs, output_path, text_column)
    
    alt text_column not in df_logs.columns
        Monitor--xClient: ValueError with available columns
    else Validation passed
        Monitor->>FS: os.makedirs(dirname(output_path))
        Monitor->>Monitor: Create ColumnMapping(text_features)
        Monitor->>Evidently: Report(metrics=[TextEvals()])
        Monitor->>Evidently: report.run(current_data=df_logs)
        Evidently-->>Monitor: Report computed
        Monitor->>Evidently: report.save_html(output_path)
        Evidently->>FS: Write HTML file
        Monitor-->>Client: output_path (str)
    end
```

---

## Figure 3: Component Diagram — Module Dependencies

*Caption: Component-level view showing the Monitoring module's external dependencies (Evidently, NLTK, pandas) and its relationship to the broader Yantra system. Verified via `import` statements in source files.*

```mermaid
flowchart TD
    subgraph "Monitoring Module"
        direction TB
        PROTO["IModelMonitor\n(Protocol)"]
        IMPL["EvidentlyQualityMonitor\n(Implementation)"]
    end

    subgraph "External Dependencies"
        direction TB
        EV["evidently\n(Report, TextEvals)"]
        NK["nltk\n(wordnet, vader, words)"]
        PD["pandas\n(DataFrame)"]
    end

    subgraph "Potential Consumers"
        direction TB
        ORC["Orchestration Module\n(@yantra_task pipeline)"]
        OBS["Observability Module\n(log_artifact for reports)"]
    end

    IMPL -->|implements| PROTO
    IMPL -->|generates reports via| EV
    IMPL -->|lazy-loads corpora from| NK
    IMPL -->|processes| PD
    PROTO -->|used by| ORC
    OBS -->|tracks artifacts from| IMPL
```

---

## Figure 4: State Diagram — Report Generation Lifecycle

*Caption: State machine showing the lifecycle of a `generate_report()` invocation, including validation, computation, serialization, and error states. Each state corresponds to a distinct operation phase.*

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Validating : generate_report() called
    Validating --> ColumnError : text_column missing
    Validating --> PreparingDirectory : validation passed
    PreparingDirectory --> MappingColumns : os.makedirs success
    MappingColumns --> ComputingMetrics : ColumnMapping created
    ComputingMetrics --> SerializingHTML : report.run() success
    ComputingMetrics --> ExecutionError : Evidently/NLTK exception
    SerializingHTML --> Idle : report.save_html() success
    SerializingHTML --> ExecutionError : I/O failure
    ColumnError --> [*] : ValueError raised
    ExecutionError --> [*] : RuntimeError raised
```

---

## Figure 5: Data Flow Diagram — NLP Processing Pipeline

*Caption: Shows how data flows from raw LLM log DataFrames through NLTK tokenization, VADER sentiment analysis, and Evidently metric aggregation to produce the final HTML report.*

```mermaid
flowchart LR
    subgraph "Input"
        DF["pd.DataFrame\n(LLM logs)"]
        TC["text_column\nspecification"]
    end

    subgraph "Validation Layer"
        COL_CHECK["Column\nExistence Check"]
        DIR_CHECK["Output Directory\nProvisioning"]
    end

    subgraph "Evidently Engine"
        CM["ColumnMapping\n(text_features)"]
        TE["TextEvals Preset"]
        subgraph "NLP Metrics"
            VADER["VADER\nSentiment"]
            OOV["OOV Ratio\n(words corpus)"]
            LEN["Text Length\nDistribution"]
            WC["Word Count\nDistribution"]
        end
    end

    subgraph "NLTK Resources"
        WN["wordnet"]
        OMW["omw-1.4"]
        VL["vader_lexicon"]
        WD["words"]
    end

    subgraph "Output"
        HTML["HTML Report\n(self-contained)"]
    end

    DF --> COL_CHECK
    TC --> COL_CHECK
    COL_CHECK --> CM
    DIR_CHECK --> HTML
    CM --> TE
    TE --> VADER
    TE --> OOV
    TE --> LEN
    TE --> WC
    VL -.->|provides lexicon| VADER
    WD -.->|provides vocabulary| OOV
    WN -.->|provides synsets| OOV
    OMW -.->|multilingual support| OOV
    VADER --> HTML
    OOV --> HTML
    LEN --> HTML
    WC --> HTML
```

---

## Figure 6: Layered Architecture — Clean Architecture Alignment

*Caption: Shows how the monitoring module adheres to Clean Architecture principles with distinct interface, implementation, and external dependency layers.*

```mermaid
flowchart TB
    subgraph "Layer 0: Interface (Stable)"
        PROTO_L["IModelMonitor Protocol\n(model_monitor_protocol.py)"]
    end

    subgraph "Layer 1: Implementation (Concrete)"
        IMPL_L["EvidentlyQualityMonitor\n(quality.py)"]
    end

    subgraph "Layer 2: External Libraries (Volatile)"
        EV_L["evidently"]
        NK_L["nltk"]
        PD_L["pandas"]
    end

    subgraph "Layer 3: OS / Network"
        FS_L["File System\n(os.makedirs, save_html)"]
        NET_L["Network\n(nltk.download)"]
    end

    PROTO_L --> IMPL_L
    IMPL_L --> EV_L
    IMPL_L --> NK_L
    IMPL_L --> PD_L
    EV_L --> FS_L
    NK_L --> NET_L
    NK_L --> FS_L

    style PROTO_L fill:#2d6a4f,color:#fff
    style IMPL_L fill:#40916c,color:#fff
    style EV_L fill:#52b788,color:#000
    style NK_L fill:#52b788,color:#000
    style PD_L fill:#52b788,color:#000
```

---

## Table 1: NLTK Resource Requirements

*Caption: NLTK corpora and lexicons required by `EvidentlyQualityMonitor`, their check paths, purpose, and approximate download size. Source: `quality.py:L26-L31`.*

| S.No | Check Path | Package Name | Purpose | Approx. Size |
|:---:|:---|:---|:---|:---|
| 1 | `corpora/wordnet` | `wordnet` | Word sense disambiguation, synonym detection | ~12 MB |
| 2 | `corpora/omw-1.4` | `omw-1.4` | Open Multilingual Wordnet for cross-language support | ~5 MB |
| 3 | `sentiment/vader_lexicon.zip` | `vader_lexicon` | VADER sentiment analysis lexicon (7,517 entries) | ~500 KB |
| 4 | `corpora/words` | `words` | English word list for OOV detection (236,736 words) | ~700 KB |

**Total cold-start download:** ~18 MB

---

## Table 2: Protocol Method Specification

*Caption: Complete specification of the `IModelMonitor` protocol. Note the `@runtime_checkable` decorator enabling `isinstance()` checks. Source: `model_monitor_protocol.py:L6-L28`.*

| S.No | Method | Parameters | Return | Purpose |
|:---:|:---|:---|:---|:---|
| 1 | `generate_report` | `df_logs: DataFrame`, `output_path: str`, `text_column: str = "response"` | `str` (path) | Generate quality report from LLM log data |

---

## Table 3: Error Handling Strategy

*Caption: Comprehensive error handling matrix showing error conditions, their detection mechanism, and recovery behavior. Verified against `quality.py:L79-L111`.*

| S.No | Error Condition | Detection | Exception Type | Recovery | Source |
|:---:|:---|:---|:---|:---|:---|
| 1 | Missing text column | `text_column not in df_logs.columns` | `ValueError` | Fail-fast with column list | `quality.py:L80-L84` |
| 2 | NLTK resource missing | `LookupError` from `nltk.data.find()` | Auto-download | Lazy acquisition | `quality.py:L41-L45` |
| 3 | Evidently computation failure | Generic `Exception` catch | `RuntimeError` (chained) | Error logged with `exc_info=True` | `quality.py:L109-L111` |
| 4 | Output directory missing | `os.makedirs(..., exist_ok=True)` | Auto-create | Idempotent provisioning | `quality.py:L87` |

---

## Table 4: TextEvals Metrics Inventory

*Caption: Complete list of NLP metrics computed by the Evidently TextEvals preset, their mathematical basis, and interpretation guidance.*

| S.No | Metric | Algorithm | Range | Good Value | Interpretation |
|:---:|:---|:---|:---|:---|:---|
| 1 | Sentiment (compound) | VADER lexicon + rules | [-1, +1] | Domain-dependent | >0.05 positive, <-0.05 negative |
| 2 | Text Length | Character count | [0, ∞) | Domain-dependent | Consistency indicator |
| 3 | OOV Ratio | Token-vs-vocabulary | [0, 1] | <0.10 | High = garbled/hallucinated output |
| 4 | Word Count | Whitespace tokenization | [0, ∞) | Domain-dependent | Response completeness |

---

## Table 5: Architectural Design Decisions

*Caption: Key architectural decisions and their rationale, tracing design intent to implementation.*

| S.No | Decision | Rationale | Alternative Considered | Trade-off |
|:---:|:---|:---|:---|:---|
| 1 | Single-method Protocol | Minimal interface; easy to implement | Multi-method interface | Simplicity vs. interface depth (see MON-GAP) |
| 2 | `@runtime_checkable` | Enables DI validation via `isinstance()` | Omit decorator | Minor runtime cost; significant DI benefit |
| 3 | Eager NLTK in constructor | Resources ready before any report call | Lazy in `generate_report` | Slower init, faster first report |
| 4 | Evidently TextEvals preset | Pre-configured, production-tested metrics | Custom VADER pipeline | Less control; more reliability |
| 5 | HTML output format | Rich visualizations, self-contained | JSON/dict | Human-readable vs. machine-readable |
| 6 | `pandas` in Protocol signature | Ubiquitous in ML; practical choice | `Any` type | Coupling vs. type safety (see MON-GAP-003) |
| 7 | Exception chaining (`from exc`) | Preserves original traceback | Re-raise original | Better debugging; standardized error type |
| 8 | Structured logging (`logger`) | Production-grade; unlike `print()` in other modules | `print()` | Best practice; enables log aggregation |
