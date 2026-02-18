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

## Table 1: NLTK Resource Requirements

*Caption: NLTK corpora and lexicons required by `EvidentlyQualityMonitor`, their check paths, and purpose. Source: `quality.py:L26-L31`.*

| S.No | Check Path | Package Name | Purpose |
|:---:|:---|:---|:---|
| 1 | `corpora/wordnet` | `wordnet` | Word sense disambiguation, synonym detection |
| 2 | `corpora/omw-1.4` | `omw-1.4` | Open Multilingual Wordnet for cross-language support |
| 3 | `sentiment/vader_lexicon.zip` | `vader_lexicon` | VADER sentiment analysis lexicon |
| 4 | `corpora/words` | `words` | English word list for OOV (Out-of-Vocabulary) detection |

---

## Table 2: Protocol Method Specification

*Caption: Complete specification of the `IModelMonitor` protocol. Note the `@runtime_checkable` decorator enabling `isinstance()` checks. Source: `model_monitor_protocol.py:L6-L28`.*

| S.No | Method | Parameters | Return | Purpose |
|:---:|:---|:---|:---|:---|
| 1 | `generate_report` | `df_logs: DataFrame`, `output_path: str`, `text_column: str = "response"` | `str` (path) | Generate quality report from LLM log data |
