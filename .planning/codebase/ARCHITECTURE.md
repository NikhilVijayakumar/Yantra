# Architecture

**Analysis Date:** 2026-04-10

## Pattern Overview

**Overall:** Protocol-Based Dependency Inversion Architecture

**Key Characteristics:**
- **Interface-First Design**: Protocols (Python's structural typing) define contracts before implementations
- **Swappable Implementations**: Domain logic depends on abstractions, not concrete tools
- **Centralized Context**: Singleton-style context (`YantraContext`) manages runtime state
- **Configuration-Driven**: All infrastructure setup via YAML configuration files

## Layers

### Protocol Layer (Interfaces)
- Purpose: Define contracts for domain operations
- Location: `src/nikhil/yantra/domain/*/ *_protocol.py`
- Contains: Abstract protocol definitions with `@runtime_checkable`
- Depends on: Python typing module only
- Used by: All implementation modules

**Protocols:**
- `IDataVersionControl` (`data_versioning/data_version_protocol.py`)
- `IExperimentTracker` (`observability/experiment_tracker_protocol.py`)
- `IModelMonitor` (`monitoring/model_monitor_protocol.py`)

### Domain Layer (Implementations)
- Purpose: Provide concrete implementations of protocols
- Location: `src/nikhil/yantra/domain/[module]/`
- Contains: Production-ready implementations
- Depends on: Protocol layer + external libraries
- Used by: Orchestration layer + user code

**Core Modules:**

| Module | Implementation | File |
|--------|----------------|------|
| data_versioning | DVCDataTracker | `domain/data_versioning/dvc_tracker.py` |
| data_versioning | DVCSetup | `domain/data_versioning/dvc_setup.py` |
| observability | MLflowTracker | `domain/observability/mlflow_tracker.py` |
| observability | ModelArena | `domain/observability/arena.py` |
| monitoring | EvidentlyQualityMonitor | `domain/monitoring/quality.py` |
| orchestration | yantra_task decorator | `domain/orchestration/prefect_utils.py` |

### Orchestration Layer
- Purpose: Combine domain operations into workflow tasks
- Location: `src/nikhil/yantra/domain/orchestration/`
- Contains: Prefect task decorators, context management
- Depends on: Domain layer + Prefect
- Used by: Workflow pipelines

**Orchestration Components:**
- `YantraContext` (`domain/orchestration/context.py`) - Global tracker singleton
- `yantra_task` (`domain/orchestration/prefect_utils.py`) - Dual-purpose decorator (Prefect + MLflow)

### Utility Layer
- Purpose: Shared helper functions
- Location: `src/nikhil/yantra/utils/`
- Contains: YAML loading, configuration parsing
- Depends on: Standard library only

## Data Flow

### Configuration Flow
```
config/mlops_config.yaml 
    → YamlUtils.yaml_safe_load()
    → Domain implementations (__init__)
    → Configured objects (DVCDataTracker, MLflowTracker, etc.)
```

### Data Versioning Flow
```
DVCDataTracker.setup() → DVCSetup
    → 1. Create directories (_create_directories)
    → 2. Verify S3 bucket (_ensure_bucket_exists)
    → 3. Configure DVC remote (_configure_dvc)
    → 4. Bootstrap data (_bootstrap_data)

DVCDataTracker.sync() → Full workflow
    → pull() → track() → git commit → push()
```

### Observability Flow
```
YantraContext.set_tracker(MLflowTracker(...))
    → Global tracker available to all yantra_task decorated functions
    
yantra_task execution:
    → Prefect task execution
    → Capture function inputs (inspect.signature)
    → start_span() wraps execution
    → Log outputs and status
    → Automatic error logging
```

### Monitoring Flow
```
DataFrame with logs → EvidentlyQualityMonitor.generate_report()
    → ColumnMapping with text_features
    → Report(metrics=[TextEvals()])
    → Generate HTML quality report
```

## Key Abstractions

**IDataVersionControl:**
- Purpose: Abstract data versioning operations
- Examples: `DVCDataTracker`
- Pattern: Protocol with implementation

**IExperimentTracker:**
- Purpose: Abstract experiment tracking + LLM tracing
- Examples: `MLflowTracker`
- Pattern: Protocol with MLflow-specific features

**IModelMonitor:**
- Purpose: Abstract model quality monitoring
- Examples: `EvidentlyQualityMonitor`
- Pattern: Protocol with swappable backends (Evidently, DeepChecks, Whylogs)

**ModelArena:**
- Purpose: LLM comparison framework
- Location: `domain/observability/arena.py`
- Pattern: MLflow Evaluate with LLM-as-a-Judge metrics

## Entry Points

**Configuration Entry:**
- Location: `config/mlops_config.yaml`
- Triggers: YAML loading via `YamlUtils`
- Responsibilities: Define paths, credentials, service endpoints

**Domain Initialization:**
- DVC: `DVCSetup(config_path).setup()`
- Tracking: `YantraContext.set_tracker(MLflowTracker(...))`
- Monitoring: `EvidentlyQualityMonitor()`

**Task Registration:**
- Location: `@yantra_task` decorator
- Triggers: Function decorated with `@yantra_task`
- Responsibilities: Register as Prefect task + wrap in MLflow span

## Error Handling

**Strategy:** Custom exception hierarchy

**Patterns:**
- `YantraDVCError` - Wraps subprocess DVC errors
- `FileNotFoundError` - Missing config files
- `yaml.YAMLError` - Malformed YAML
- Context manager fallbacks in `mlflow_tracker.py`

**Observer Pattern in Tasks:**
- `yantra_task` decorator automatically captures and logs exceptions to MLflow trace before re-raising

## Cross-Cutting Concerns

**Logging:** MLflow for experiments; Prefect logger for tasks
**Validation:** YAML schema validation; NLTK resource verification in monitoring
**Authentication:** S3 credentials in config; MLflow tracking URI