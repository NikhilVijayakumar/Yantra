# Codebase Structure

**Analysis Date:** 2026-04-10

## Directory Layout

```
/home/dell/PycharmProjects/Yantra/
├── .planning/codebase/          # Analysis output (this directory)
├── build/                      # Build artifacts
├── config/                    # Configuration files
│   └── mlops_config.yaml     # Main MLOps configuration
├── data/                      # Data directories
│   ├── input/                # Input data (DVC tracked)
│   └── output/               # Output data (DVC tracked)
├── .dvc/                      # DVC metadata
├── docs/                      # Documentation
├── src/                       # Source code
│   └── nikhil/              # Package root
│       └── yantra/          # Main package
│           ├── domain/     # Domain modules
│           │   ├── data_versioning/
│           │   ├── monitoring/
│           │   ├── observability/
│           │   └── orchestration/
│           └── utils/      # Utility modules
│               └── yaml_utils.py
├── docker-compose.yml        # Docker services
├── pyproject.toml            # Package configuration
└── README.md
```

## Directory Purposes

### `src/nikhil/yantra/domain/`
- **Purpose:** Core domain modules implementing MLOps operations
- **Contains:** Protocol definitions and implementations
- **Key files:** `__init__.py` files export public API

### `config/`
- **Purpose:** Application configuration
- **Contains:** YAML config files
- **Key files:** `mlops_config.yaml`

### `data/`
- **Purpose:** Data storage
- **Contains:** Input/output datasets
- **Generated:** Yes (at runtime)
- **Note:** DVC-tracked directories

## Key File Locations

### Entry Points
- **Configuration:** `config/mlops_config.yaml` - YAML configuration for all services
- **Initialization:** `src/nikhil/yantra/domain/data_versioning/dvc_setup.py` - Infrastructure setup

### Protocol Files (Interfaces)
| Protocol | File Path |
|----------|------------|
| IDataVersionControl | `src/nikhil/yantra/domain/data_versioning/data_version_protocol.py` |
| IExperimentTracker | `src/nikhil/yantra/domain/observability/experiment_tracker_protocol.py` |
| IModelMonitor | `src/nikhil/yantra/domain/monitoring/model_monitor_protocol.py` |

### Domain Implementation Files
| Module | Implementation | File Path |
|--------|----------------|-----------|
| data_versioning | DVCDataTracker | `src/nikhil/yantra/domain/data_versioning/dvc_tracker.py` |
| data_versioning | DVCSetup | `src/nikhil/yantra/domain/data_versioning/dvc_setup.py` |
| data_versioning | YantraDVCError | `src/nikhil/yantra/domain/data_versioning/dvc_setup.py` |
| observability | MLflowTracker | `src/nikhil/yantra/domain/observability/mlflow_tracker.py` |
| observability | ModelArena | `src/nikhil/yantra/domain/observability/arena.py` |
| monitoring | EvidentlyQualityMonitor | `src/nikhil/yantra/domain/monitoring/quality.py` |
| orchestration | YantraContext | `src/nikhil/yantra/domain/orchestration/context.py` |
| orchestration | yantra_task | `src/nikhil/yantra/domain/orchestration/prefect_utils.py` |
| utils | YamlUtils | `src/nikhil/yantra/utils/yaml_utils.py` |

### `__init__.py` Files (Public API)
| Module | Exports |
|--------|---------|
| `data_versioning/__init__.py` | `IDataVersionControl`, `DVCSetup`, `DVCDataTracker`, `YantraDVCError` |
| `observability/__init__.py` | `IExperimentTracker`, `MLflowTracker`, `ModelArena` |
| `monitoring/__init__.py` | `IModelMonitor`, `EvidentlyQualityMonitor` |
| `orchestration/__init__.py` | `yantra_task` |

## Naming Conventions

### Files
- **Protocols:** `*_protocol.py` (e.g., `data_version_protocol.py`)
- **Implementations:** `*_tracker.py`, `*_setup.py`, `*_monitor.py`, `quality.py`
- **Utilities:** `*_utils.py`

### Directories
- **Domain modules:** lowercase with underscores (e.g., `data_versioning`, `model_monitor`)
- **Configuration:** singular (e.g., `config/`)

### Classes
- **Protocols:** `I*` prefix (e.g., `IDataVersionControl`)
- **Errors:** `*Error` suffix (e.g., `YantraDVCError`)
- **Utilities:** `*Utils` suffix (e.g., `YamlUtils`)

### Functions/Decorators
- **Decorators:** snake_case (e.g., `yantra_task`)
- **Helper functions:** snake_case (e.g., `_run_command`, `_ensure_nltk_resources`)

## Where to Add New Code

### New Protocol (Interface)
- **Primary code:** `src/nikhil/yantra/domain/[module]/_protocol.py`
- **Pattern:** Use `@runtime_checkable Protocol` with typed method signatures

### New Domain Implementation
- **Primary code:** `src/nikhil/yantra/domain/[module]/[implementation].py`
- **Tests:** Co-located test file or separate test directory
- **Export:** Add to `domain/[module]/__init__.py`

### New Utility
- **Implementation:** `src/nikhil/yantra/utils/[name]_utils.py`
- **Export:** Add to `utils/__init__.py`

### New Configuration
- **Configuration:** `config/[name]_config.yaml`
- **Loader:** Use existing `YamlUtils.yaml_safe_load()`

## Special Directories

### `data/`
- **Purpose:** Data storage for DVC version control
- **Contains:** Input/output datasets
- **Generated:** Yes (at runtime or by DVC pull)
- **Committed:** No (tracked by DVC, not Git)

### `.dvc/`
- **Purpose:** DVC metadata directory
- **Generated:** Yes (by DVC initialization)
- **Committed:** Yes

### `build/`
- **Purpose:** Build artifacts
- **Generated:** Yes (by build tools)
- **Committed:** Typically no (.gitignore)

## Module Dependency Graph

```
                    ┌─────────────────────────────────────────┐
                    │          Orchestration Layer           │
                    │  (prefect_utils.py, context.py)       │
                    │         Depends on: all domains     │
                    └──────────────┬──────────────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│    Data      │         │  Observability│        │  Monitoring  │
│  Versioning  │         │   (MLflow)   │        │  (Evidently) │
│   (DVC)      │         │              │         │              │
└───────────────┘         └───────────────┘         └───────────────┘
        │                          │                          │
        └──────────────────────────┴──────────────────────────┘
                                   │
                    ┌──────────────┴──────────────────────┐
                    │            Protocol Layer             │
                    │     (data_version_protocol.py,       │
                    │  experiment_tracker_protocol.py,    │
                    │      model_monitor_protocol.py)     │
                    └──────────────────────────────────────┘
                                   │
                    ┌──────────────┴──────────────────────┐
                    │           Utility Layer             │
                    │          (yaml_utils.py)            │
                    └──────────────────────────────────────┘
```