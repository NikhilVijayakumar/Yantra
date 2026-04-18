# Cross-Module Analysis — Research Gaps

## 1. System-Level Gap Summary

| S.No | Gap ID | Severity | Scope | Description | Modules Affected | Effort |
|:---:|:---|:---|:---|:---|:---|:---|
| 1 | SYS-GAP-001 | **Critical** | System-wide | Zero test coverage across all 4 modules (0/782 LOC tested) | All 4 | 15-20 days |
| 2 | SYS-GAP-002 | **Critical** | System-wide | No integration tests verifying cross-module interactions | orchestration ↔ observability | 5-7 days |
| 3 | SYS-GAP-003 | **Moderate** | System-wide | Protocol purity violations — 2/3 Protocols import external libraries | observability, monitoring | 0.5 days |
| 4 | SYS-GAP-004 | **Moderate** | System-wide | Zero alternative implementations for any Protocol (0/3) | observability, monitoring, data_versioning | 5-7 days |
| 5 | SYS-GAP-005 | **Moderate** | Architecture | Inconsistent `@runtime_checkable` decorator usage (2/3 Protocols) | observability | 5 min |
| 6 | SYS-GAP-006 | **Moderate** | Architecture | No shared error handling strategy — 4 different approaches | All 4 | 2-3 days |
| 7 | SYS-GAP-007 | **Moderate** | Security | Credentials stored in plaintext config (data_versioning) | data_versioning | 1-2 days |
| 8 | SYS-GAP-008 | **Minor** | Architecture | No shared logging framework — modules use `print()`, `logger`, or silent fail | All 4 | 2-3 days |
| 9 | SYS-GAP-009 | **Minor** | Architecture | Code duplication across modules (config loading, `_run_command`) | data_versioning | 1 day |
| 10 | SYS-GAP-010 | **Minor** | API | Inconsistent `__init__.py` documentation and export patterns | All 4 | 0.5 days |

---

## 2. System-Level Scopus Readiness

| Criterion | Status | Evidence |
|:---|:---|:---|
| **Reproducibility** | ❌ **Fail** | 0% test coverage across entire system |
| **Core Claims** | ⚠️ Partial | Protocol-first architecture exists but never validated (no swaps, no tests) |
| **Clean Architecture** | ⚠️ Partial | 2/3 Protocol purity violations undermine DIP claims |
| **Integration Proof** | ❌ **Fail** | Orchestration ↔ Observability bridge untested end-to-end |
| **Security** | ❌ **Fail** | Plaintext credentials in config (DV-GAP-002) |
| **Completeness** | ⚠️ Partial | No async support, no drift detection, no flow-level orchestration |
| **System-Level Scopus Readiness** | **~30%** | Critical path: tests → Protocol fixes → integration tests |

### Per-Module Scopus Readiness Comparison

| Module | Readiness | Critical Gaps | Blocking Issue |
|:---|:---:|:---:|:---|
| `observability` | 35% | 2 | No tests + Protocol imports `mlflow` |
| `data_versioning` | 35% | 2 | No tests + insecure credentials |
| `orchestration` | 30% | 2 | No tests + no integration test |
| `monitoring` | 30% | 2 | No tests + no drift detection |
| **System Average** | **32.5%** | **8** | **0/4 modules have any tests** |

---

## 3. Critical System Gaps

### SYS-GAP-001: Zero Test Coverage Across Entire System

**Evidence:** `find tests/ -name "*.py" | xargs grep -l "yantra"` → **0 results**

**Quantitative Impact:**

| Module | Source LOC | Test LOC | Coverage | Untested Entry Points |
|:---|:---:|:---:|:---:|:---:|
| `observability` | 210 | 0 | 0% | 13 |
| `orchestration` | 96 | 0 | 0% | 4 |
| `monitoring` | 146 | 0 | 0% | 4 |
| `data_versioning` | 280 | 0 | 0% | 11 |
| **Total** | **732** | **0** | **0%** | **32** |

**Cross-Module Impact:** Without tests, no claim in the paper — Protocol swappability, decorator correctness, defensive error handling, idempotent provisioning — has empirical support.

**Remediation:**

| Phase | Tests | Effort | Modules |
|:---|:---|:---|:---|
| Phase 1 | Unit tests (mocked externals) | 10-14 days | All 4 |
| Phase 2 | Integration tests (real backends) | 3-4 days | orchestration ↔ observability |
| Phase 3 | End-to-end pipeline test | 2-3 days | All 4 |
| **Total** | | **15-21 days** | |

---

### SYS-GAP-002: No Cross-Module Integration Tests

**Evidence:** The `@yantra_task` decorator is the system's **only inter-module dependency** — it bridges orchestration and observability. This bridge has never been tested end-to-end.

**Integration Points to Test:**

| S.No | Integration | From → To | Verification |
|:---:|:---|:---|:---|
| 1 | `@yantra_task` + `MLflowTracker` | orchestration → observability | Span created with correct inputs/outputs |
| 2 | `@yantra_task` + retry | orchestration → observability | Multiple spans on failure |
| 3 | `MLflowTracker.log_artifact` + report | observability → monitoring output | Artifact logged correctly |
| 4 | `DVCDataTracker.sync` + `YantraContext` | data_versioning + orchestration | Version tracked within pipeline |

**Remediation:**
1. Create `tests/integration/test_orchestration_observability.py`
2. Use real Prefect (local mode) + MLflow (file store)
3. Verify span creation, error handling, and retry-trace interaction

**Estimated Effort:** 5-7 days

---

## 4. Moderate System Gaps

### SYS-GAP-003: Protocol Purity Violations

**Evidence:** 2 of 3 Protocols import external implementation libraries, violating the Dependency Inversion Principle:

| Protocol | External Import | File | Severity |
|:---|:---|:---|:---|
| `IExperimentTracker` | `import mlflow` | `experiment_tracker_protocol.py:L3` | ⚠️ Unused import |
| `IModelMonitor` | `import pandas as pd` | `model_monitor_protocol.py:L3` | ⚠️ Used in method signature |
| `IDataVersionControl` | ✅ None | `data_version_protocol.py` | Clean |

**Impact on Paper:** The paper's core claim is "Protocol-first, implementation-agnostic architecture." Having implementation-specific imports in Protocol files directly contradicts this claim.

**Remediation:**
1. Remove `import mlflow` from `experiment_tracker_protocol.py` (unused) — 5 min
2. Replace `pd.DataFrame` with `Any` or a custom type alias in `model_monitor_protocol.py` — 15 min
3. Verify all implementations still pass structural subtyping checks

---

### SYS-GAP-004: No Alternative Implementations

**Evidence:** Every Protocol has exactly 1 implementation. No mock, null, or alternative backend exists:

| Protocol | Current Implementation | Missing Alternatives |
|:---|:---|:---|
| `IExperimentTracker` | `MLflowTracker` | `NullTracker`, `WandbTracker`, `InMemoryTracker` |
| `IModelMonitor` | `EvidentlyQualityMonitor` | `NullMonitor`, `DeepChecksMonitor` |
| `IDataVersionControl` | `DVCDataTracker` | `LocalFileTracker`, `NullTracker` |

**Impact on Paper:** The Protocol-first architecture's value proposition is backend swappability. Without a second implementation, this is an architectural promise, not a demonstrated capability.

**Minimum Viable Validation:**
1. Create `NullTracker(IExperimentTracker)` — no-op implementation (0.5 days)
2. Create `NullMonitor(IModelMonitor)` — no-op implementation (0.5 days)
3. Create `InMemoryTracker` for testing (1-2 days)

---

### SYS-GAP-006: Inconsistent Error Handling Strategy

**Evidence:** The 4 modules use 4 different error handling approaches:

| Module | Primary Strategy | Example | Risk |
|:---|:---|:---|:---|
| `observability` | **Silent failure** — `except: print()` | `mlflow_tracker.py:L33` | Hides problems |
| `orchestration` | **Re-raise** — `except: span.error → raise` | `prefect_utils.py:L61` | Correct but inconsistent |
| `monitoring` | **Exception chaining** — `raise from exc` | `quality.py:L109` | Best practice |
| `data_versioning` | **Domain exception** — `raise YantraDVCError` | `dvc_setup.py:L21` | Custom but inconsistent |

**Recommendation:** Establish a Yantra-wide error handling policy:
1. Never use silent `print()` for errors (fix observability)
2. Use exception chaining for all wrapped errors
3. Define domain exceptions per module (like `YantraDVCError`)

---

## 5. Minor System Gaps

### SYS-GAP-008: No Shared Logging Framework

| Module | Logging Method | Issues |
|:---|:---|:---|
| `observability` | `print()` statements | No log levels, no structured output |
| `orchestration` | `prefect.get_run_logger()` | Prefect-specific, not available outside flows |
| `monitoring` | `raise RuntimeError` (no logging) | No operational logging at all |
| `data_versioning` | None (subprocess output) | No visibility into operations |

**Recommendation:** Adopt Python's `logging` module with a shared `yantra` logger hierarchy.

### SYS-GAP-009: Code Duplication in Data Versioning

Both `DVCSetup` and `DVCDataTracker` independently implement:
- Configuration loading via `YamlUtils.yaml_safe_load(config_path)`
- `_run_command` helper for subprocess execution
- Config path validation guards

**Recommendation:** Extract a shared `DVCBase` class or utility module.

---

## 6. Cross-Module Gap Aggregation

### Gap Severity Distribution

| Severity | Per-Module Total | System-Level | Grand Total |
|:---|:---:|:---:|:---:|
| **Critical** | 8 (2 per module) | 2 | **10** |
| **Moderate** | 16 (4 per module) | 5 | **21** |
| **Minor** | 16 (4 per module) | 3 | **19** |
| **Total** | **40** | **10** | **50** |

### Remediation Effort Summary

| Priority | Gap IDs | Description | Effort |
|:---|:---|:---|:---|
| **P0 (Blocks publication)** | SYS-GAP-001, SYS-GAP-002, SYS-GAP-003 | Tests + Protocol purity | 21-28 days |
| **P1 (Weakens claims)** | SYS-GAP-004, SYS-GAP-005 | Alternative implementations + consistency | 5-8 days |
| **P2 (Production concern)** | SYS-GAP-006, SYS-GAP-007 | Error handling + security | 3-5 days |
| **P3 (Enhancement)** | SYS-GAP-008, SYS-GAP-009, SYS-GAP-010 | Logging + dedup + API | 3.5-4.5 days |
| **Total** | | | **32.5-45.5 days** |

### Gap Overlap Analysis

Many per-module gaps are instances of the same system-level gap:

| System Gap | Per-Module Instances |
|:---|:---|
| SYS-GAP-001 (No tests) | OBS-GAP-001, ORC-GAP-001, MON-GAP-001, DV-GAP-001 |
| SYS-GAP-003 (Protocol impurity) | OBS-GAP-002, MON-GAP-003 |
| SYS-GAP-005 (Inconsistent `@runtime_checkable`) | OBS-GAP-010 |
| SYS-GAP-007 (Security) | DV-GAP-002 |

Fixing 4 system-level gaps resolves 10 per-module gaps — a **40% dedup ratio**.
