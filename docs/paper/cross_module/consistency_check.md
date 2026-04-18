# Cross-Module Analysis — Consistency Check

## 1. Data Format Consistency Matrix

*Caption: Verifies that data types and exchange formats are consistent across module boundaries. Checked at all inter-module interaction points.*

### Input/Output Type Consistency

| Module | Input Type | Output Type | Config Format | Error Type |
|:---|:---|:---|:---|:---|
| `observability` | `str`, `Dict`, `pd.DataFrame` | `MLflow Run`, `Span`, `Dict` | Constructor params | `Exception` (silent) |
| `orchestration` | `*args, **kwargs` (any) | Passthrough `Any` | Decorator params | Re-raised original |
| `monitoring` | `pd.DataFrame`, `str`, `Path` | `Path` (HTML report) | Constructor params | `RuntimeError` (chained) |
| `data_versioning` | `Path`, `str` | `None` / `subprocess` result | YAML file (`config.yaml`) | `YantraDVCError` |
| `utils` | `Path` | `Dict` (parsed YAML) | — | `Exception` (propagated) |

### Type Compatibility at Module Boundaries

| S.No | Boundary | Producer → Type → Consumer | Compatible? | Notes |
|:---:|:---|:---|:---:|:---|
| 1 | orchestration → observability | `YantraContext → IExperimentTracker → @yantra_task` | ✅ | Type annotation matches |
| 2 | data_versioning → utils | `DVCSetup → Path → YamlUtils` | ✅ | Both use `pathlib.Path` |
| 3 | monitoring → observability (potential) | `EvidentlyQualityMonitor → Path → MLflowTracker.log_artifact` | ✅ | Path string compatible |
| 4 | data_versioning → observability (potential) | `DVCDataTracker → hash → MLflowTracker.log_dataset` | ⚠️ | Requires conversion layer |

**Finding:** Current inter-module boundaries use compatible types. All modules use `pathlib.Path` for filesystem paths and Python standard types for data exchange.

---

## 2. Import Path Consistency Audit

*Caption: Verifies that all inter-module imports follow consistent patterns and respect architectural boundaries.*

### Import Pattern Analysis

| S.No | Source File | Import Statement | Target | Pattern | Valid? |
|:---:|:---|:---|:---|:---|:---:|
| 1 | `orchestration/context.py:L4` | `from ..observability ... import IExperimentTracker` | Protocol | Relative import | ✅ |
| 2 | `orchestration/prefect_utils.py:L6` | `from .context import YantraContext` | Internal | Relative import | ✅ |
| 3 | `data_versioning/dvc_setup.py:L9` | `from ...utils ... import YamlUtils` | Shared utility | Relative import | ✅ |
| 4 | `data_versioning/dvc_tracker.py:L7` | `from ...utils ... import YamlUtils` | Shared utility | Relative import | ✅ |
| 5 | `observability/experiment_tracker_protocol.py:L3` | `import mlflow` | External SDK | Absolute import | ⚠️ |
| 6 | `monitoring/model_monitor_protocol.py:L3` | `import pandas as pd` | External SDK | Absolute import | ⚠️ |

### Import Consistency Assessment

| Criterion | Result | Details |
|:---|:---:|:---|
| Consistent use of relative imports for internal modules | ✅ | All 4 inter-module imports use relative paths |
| No circular imports | ✅ | Dependency graph is acyclic |
| Protocol files free of external imports | ⚠️ 1/3 | Only `IDataVersionControl` is clean |
| `__init__.py` export consistency | ✅ | All modules define `__all__` |
| Standard library imports above third-party | ✅ | PEP 8 compliant across all modules |

---

## 3. Platform Portability Verification

| S.No | Concern | Module(s) | Status | Notes |
|:---:|:---|:---|:---:|:---|
| 1 | `pathlib.Path` usage | All | ✅ | Cross-platform path handling |
| 2 | `subprocess.run` with shell commands | `data_versioning` | ⚠️ | Uses `shell=True` — Windows compatibility concern |
| 3 | CLI tool dependencies (`dvc`, `git`) | `data_versioning` | ⚠️ | Requires CLI tools on PATH |
| 4 | File system operations | `data_versioning`, `monitoring` | ✅ | `Path.mkdir(parents=True)` — portable |
| 5 | NLTK data download | `monitoring` | ⚠️ | Requires internet on first run |
| 6 | MLflow tracking URI | `observability` | ✅ | Supports local and remote URIs |
| 7 | S3/MinIO connectivity | `data_versioning` | ⚠️ | `boto3` requires AWS credentials |
| 8 | Python version | All | ✅ | Python ≥ 3.9 (Protocol support) |

### Portability Score

| Platform | Score | Blocking Issues |
|:---|:---:|:---|
| Linux | ★★★★★ | None |
| macOS | ★★★★★ | None |
| Windows | ★★★★☆ | `subprocess` shell commands may need adaptation |
| Docker/CI | ★★★★☆ | NLTK download on cold start; S3 credentials |
| Air-gapped | ★★☆☆☆ | NLTK, MLflow, S3, DVC all need network |

---

## 4. Quality Monitoring Preset Consistency

*Caption: Verifies that quality thresholds, configuration defaults, and operational presets are consistent across modules.*

### Configuration Approach

| Module | Config Method | Config Source | Defaults | Overridable? |
|:---|:---|:---|:---|:---:|
| `observability` | Constructor params | Python kwargs | `tracking_uri`, `experiment_name` | ✅ |
| `orchestration` | Decorator params | Python kwargs | `retries=3`, `delay=5`, `log_prints=True` | ✅ |
| `monitoring` | Constructor params | Python kwargs | `text_column`, `output_path` | ✅ |
| `data_versioning` | YAML config file | `config.yaml` via `YamlUtils` | `root_dir`, `s3_config` | ✅ |
| **Consistency** | **Mixed** | 3 use kwargs, 1 uses YAML | | |

### Configuration Consistency Issues

| S.No | Issue | Modules | Severity | Recommendation |
|:---:|:---|:---|:---|:---|
| 1 | Mixed config approaches (kwargs vs. YAML) | All | Minor | Acceptable — YAML suits complex config |
| 2 | No shared config schema or validation | All | Moderate | Consider Pydantic for config validation |
| 3 | Magic numbers not extracted | orchestration (1000), monitoring (NLTK thresholds) | Minor | Extract to named constants |
| 4 | No environment variable support | All | Minor | Add `os.getenv()` fallbacks for credentials |

---

## 5. Error Message Consistency Verification

### Error Message Patterns

| Module | Error Format | Example | Structured? |
|:---|:---|:---|:---:|
| `observability` | `print(f"Error: {e}")` | `"Error logging dataset: ..."` | ❌ |
| `orchestration` | `logger.warning(f"...")` | `"No tracker found"` | ⚠️ (Prefect logger) |
| `monitoring` | `raise RuntimeError(f"...") from exc` | `"Failed to generate ... : {exc}"` | ✅ |
| `data_versioning` | `raise YantraDVCError(f"...")` | `"Config file not found: {path}"` | ✅ |

### Error Handling Quality Matrix

| Criterion | observability | orchestration | monitoring | data_versioning |
|:---|:---:|:---:|:---:|:---:|
| Uses structured exceptions | ❌ | ⚠️ | ✅ | ✅ |
| Preserves exception chain | ❌ | ✅ (re-raise) | ✅ (`from exc`) | ❌ |
| Includes context in message | ❌ | ✅ | ✅ | ✅ |
| Uses domain-specific exception | ❌ | ❌ | ❌ (`RuntimeError`) | ✅ (`YantraDVCError`) |
| Logs before raising | ❌ | ✅ | ❌ | ❌ |
| **Module Score** | **1/5** | **3/5** | **3/5** | **3/5** |

---

## 6. Overall Consistency Scorecard

| S.No | Category | Score | Grade | Key Issue |
|:---:|:---|:---:|:---:|:---|
| 1 | **Data Format Consistency** | 9/10 | **A** | All boundaries type-compatible |
| 2 | **Import Path Consistency** | 8/10 | **A-** | 2 Protocol purity violations |
| 3 | **Platform Portability** | 7/10 | **B+** | CLI deps + network requirements |
| 4 | **Configuration Consistency** | 6/10 | **B** | Mixed approaches (kwargs vs. YAML), no Pydantic |
| 5 | **Error Handling Consistency** | 5/10 | **C+** | 4 different strategies, 1 uses `print()` |
| 6 | **API Surface Consistency** | 8/10 | **A-** | All use `__all__`; 1 missing docstring |
| 7 | **Architectural Template Adherence** | 9/10 | **A** | 3/4 full compliance, orchestration justified |
| 8 | **Protocol Design Consistency** | 5/10 | **C+** | Method count variance (1-11), purity violations |
| | **Overall Score** | **57/80** | **B (71.3%)** | |

### Grade Interpretation

| Grade | Range | Meaning |
|:---|:---:|:---|
| A | 90-100% | Publication-ready, no remediation needed |
| B | 70-89% | **Current level** — needs targeted fixes |
| C | 50-69% | Significant inconsistencies, requires rework |
| D | Below 50% | Fundamental issues, major refactoring needed |

### Priority Remediation Path

| Priority | Action | Categories Improved | Effort |
|:---|:---|:---|:---|
| P0 | Fix Protocol purity (remove `import mlflow`, `import pandas`) | Import, Protocol | 0.5 days |
| P0 | Add `@runtime_checkable` to `IExperimentTracker` | Protocol | 5 min |
| P1 | Replace `print()` errors with structured exceptions in observability | Error Handling | 0.5 days |
| P1 | Standardize error handling: domain exceptions + exception chaining | Error Handling | 1-2 days |
| P2 | Add Pydantic config models per module | Configuration | 2-3 days |
| P3 | Add `__init__.py` docstrings to all modules | API Surface | 0.5 days |
| **Total** | | Score increase: ~**B → A-** | **4.5-6.5 days** |
