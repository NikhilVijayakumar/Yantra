# Cross-Module Analysis — Recurring Patterns

## 1. Pattern Summary

| S.No | Pattern | Modules Using It | Classification |
|:---:|:---|:---|:---|
| 1 | Protocol-Based Abstraction | observability, monitoring, data_versioning | **System-Wide** |
| 2 | Singleton Context | orchestration | Module-Specific |
| 3 | Decorator-Based Instrumentation | orchestration | Module-Specific |
| 4 | Lazy Resource Acquisition | monitoring | Module-Specific |
| 5 | Idempotent Provisioning | data_versioning | Module-Specific |
| 6 | Separation of Concerns (Setup vs. Workflow) | data_versioning | Module-Specific |
| 7 | Defensive Programming (Guard Clauses) | monitoring, data_versioning, orchestration | **System-Wide** |

---

## 2. System-Wide Pattern: Protocol-Based Abstraction

### Description

The **dominant architectural pattern** across Yantra is the use of Python `Protocol` classes (PEP 544 — Structural Subtyping) to decouple interfaces from implementations. Every domain module defines its own Protocol.

### Instances

| S.No | Protocol | Module | Methods | `@runtime_checkable` | Source |
|:---:|:---|:---|:---:|:---:|:---|
| 1 | `IExperimentTracker` | observability | 11 | ❌ | `experiment_tracker_protocol.py:L7` |
| 2 | `IModelMonitor` | monitoring | 1 | ✅ | `model_monitor_protocol.py:L7` |
| 3 | `IDataVersionControl` | data_versioning | 5 | ✅ | `data_version_protocol.py:L7` |

### Consistency Analysis

| Aspect | IExperimentTracker | IModelMonitor | IDataVersionControl |
|:---|:---|:---|:---|
| Uses `Protocol` | ✅ | ✅ | ✅ |
| `@runtime_checkable` | ❌ | ✅ | ✅ |
| Pure (no imports) | ⚠️ imports `mlflow` | ⚠️ imports `pandas` | ✅ clean |
| Method count | 11 (comprehensive) | 1 (minimal) | 5 (balanced) |
| Has impl. in module | ✅ `MLflowTracker` | ✅ `EvidentlyQualityMonitor` | ✅ `DVCDataTracker` |
| Has alt. implementation | ❌ | ❌ | ❌ |

### Findings

1. **Inconsistent `@runtime_checkable`**: 2 of 3 Protocols use it, but `IExperimentTracker` does not. This should be standardized.
2. **Purity violations**: 2 of 3 Protocols import external libraries (`mlflow`, `pandas`) — only `IDataVersionControl` is implementation-free.
3. **No alternative implementations**: None of the 3 Protocols have a second implementation to demonstrate swappability — the core claim.

---

## 3. System-Wide Pattern: Defensive Programming

### Description

Multiple modules implement **guard clauses** and fail-fast validation to prevent errors from propagating through the system.

### Instances

| S.No | Location | Guard | Error Response |
|:---:|:---|:---|:---|
| 1 | `quality.py:L80-L84` | `text_column not in df_logs.columns` | `ValueError` with available columns |
| 2 | `dvc_tracker.py:L59-L64` | `not target.exists()` | Auto-create directory + `.gitkeep` |
| 3 | `dvc_tracker.py:L50-L52` | `not (root_dir / ".dvc").exists()` | Skip pull, return early |
| 4 | `prefect_utils.py:L43-L45` | `tracker is None` | Graceful degradation (run without tracing) |
| 5 | `dvc_setup.py:L21-L22` | `not config_path.exists()` | `YantraDVCError` |
| 6 | `dvc_tracker.py:L18-L19` | `not config_path.exists()` | `YantraDVCError` |

---

## 4. Module-Specific Patterns

### Pattern: Singleton Context (Orchestration)

**Source:** `context.py:L7-L20`

```python
class YantraContext:
    _tracker: Optional[IExperimentTracker] = None  # Class-level state

    @classmethod
    def set_tracker(cls, tracker): ...

    @classmethod
    def get_tracker(cls): ...
```

**Purpose:** Eliminates the need to pass tracker instances through every function call. Creates an ambient context for observability.

**Trade-off:** Thread-unsafe. Should use `contextvars.ContextVar` for production.

---

### Pattern: Decorator-Based Instrumentation (Orchestration)

**Source:** `prefect_utils.py:L9-L70`

**Purpose:** Single annotation (`@yantra_task`) bridges two systems (Prefect + MLflow). Uses `functools.wraps` for metadata preservation and `inspect.signature` for argument introspection.

**Trade-off:** Only supports synchronous functions. No `async` variant exists.

---

### Pattern: Lazy Resource Acquisition (Monitoring)

**Source:** `quality.py:L39-L55`

**Purpose:** NLTK corpora are downloaded only when missing. Optimized for Docker/CI where resources are pre-cached in the image.

**Trade-off:** First-run latency if resources are not cached. No retry logic for failed downloads.

---

### Pattern: Infrastructure vs. Workflow Separation (Data Versioning)

**Source:** `dvc_setup.py` (infrastructure) ↔ `dvc_tracker.py` (workflow)

**Purpose:** One-time setup (S3 buckets, DVC remote) is cleanly separated from day-to-day operations (track, push, pull, sync). `DVCDataTracker.setup()` delegates to `DVCSetup` via composition.

**Trade-off:** Code duplication between the two classes (`_run_command`, config loading).

---

## 5. Protocol Compliance Score

| S.No | Criterion | Result | Score |
|:---:|:---|:---|:---:|
| 1 | All modules define a Protocol | ✅ 3/3 domain modules | 10/10 |
| 2 | All Protocols have implementations | ✅ 3/3 | 10/10 |
| 3 | Consistent `@runtime_checkable` | ⚠️ 2/3 | 7/10 |
| 4 | Protocols are implementation-free | ⚠️ 1/3 clean | 3/10 |
| 5 | Alternative implementations exist | ❌ 0/3 | 0/10 |
| 6 | Protocols exported via `__init__.py` | ✅ 3/3 | 10/10 |
| | **Total** | | **40/60 (67%)** |

### Remediation Priority

1. **Add `@runtime_checkable` to `IExperimentTracker`** — 5 minutes
2. **Remove `import mlflow` from `experiment_tracker_protocol.py`** — 5 minutes  
3. **Remove `import pandas` from `model_monitor_protocol.py`** or accept as pragmatic choice — 10 minutes
4. **Create `NullTracker`, `NullMonitor`, `LocalFileTracker`** — 2-3 days (critical for publication)
