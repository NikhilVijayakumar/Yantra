# Monitoring Module - Research Gap Analysis

## Gap Summary

| S.No | Gap ID | Severity | Description | Effort | Scopus Impact |
|:---:|:---|:---|:---|:---|:---|
| 1 | MON-GAP-001 | **Critical** | No unit tests for any component | 3 days | Blocks publication |
| 2 | MON-GAP-002 | **Critical** | No reference data support (drift detection impossible) | 2-3 days | Core feature missing |
| 3 | MON-GAP-003 | **Moderate** | Protocol imports `pandas` (couples interface to implementation detail) | 1 day | Weakens Clean Architecture claims |
| 4 | MON-GAP-004 | **Moderate** | Only text metrics supported; no numerical/tabular monitoring | 2 days | Limits generalizability |
| 5 | MON-GAP-005 | **Moderate** | No configurable metric selection (TextEvals hardcoded) | 1 day | Inflexible for users |
| 6 | MON-GAP-006 | **Moderate** | No threshold-based alerting or programmatic metric access | 1-2 days | Production readiness |
| 7 | MON-GAP-007 | **Minor** | Uses legacy `ColumnMapping` import path | 0.5 days | Maintenance risk |
| 8 | MON-GAP-008 | **Minor** | No report format options (HTML only) | 1 day | Machine-consumption barrier |
| 9 | MON-GAP-009 | **Minor** | No data sampling for large DataFrames | 1 day | Scalability gap |
| 10 | MON-GAP-010 | **Minor** | Single-method Protocol insufficient for interface depth | 1-2 days | Weakens Protocol claims |

---

## Scopus-Readiness Assessment

| Criterion | Status | Notes |
|:---|:---|:---|
| **Reproducibility** | ❌ Fail | No tests (MON-GAP-001); no benchmark data |
| **Core Feature** | ❌ Fail | No drift detection (MON-GAP-002); profiling only |
| **Generalizability** | ⚠️ Partial | Text-only monitoring (MON-GAP-004); no numerical support |
| **Code Quality** | ✅ Pass | Uses `logging` (not `print()`); proper exception chaining |
| **Extensibility** | ⚠️ Partial | Hardcoded metrics (MON-GAP-005); no format options (MON-GAP-008) |
| **Production Readiness** | ⚠️ Partial | No alerts (MON-GAP-006); no sampling (MON-GAP-009) |

**Overall Scopus Readiness: 30%** — Critical gaps must be resolved before submission.

---

## Critical Gaps

### MON-GAP-001: No Unit Tests

**Source:** Verified via `find tests/ -name "*monitoring*" -o -name "*quality*" -o -name "*monitor*"` — **0 results**

**Impact:** Blocks publication. The core pipeline logic (validation, NLTK loading, Evidently report generation) is fully untested. Without mocked tests, there is no evidence that the code handles edge cases (empty DataFrame, missing column, NLTK download failure).

**Quantitative Impact:**
- **Test coverage:** 0% (0/112 lines in `quality.py`, 0/28 lines in `model_monitor_protocol.py`)
- **Untested code paths:** 8 (column validation, NLTK check, NLTK download, report creation, report run, HTML save, exception handling, directory creation)
- **Risk surface:** 1 Protocol method + 2 private methods + 1 constructor = 4 untested entry points

**Recommendation:**
1. Create `tests/unit/monitoring/test_quality_monitor.py`:
   - Mock `evidently.Report` and `nltk.data.find` / `nltk.download`
   - Test `generate_report` with valid inputs → verify HTML path returned
   - Test with missing `text_column` → verify `ValueError` raised with diagnostic columns
   - Test with empty DataFrame → verify behavior
   - Test NLTK lazy loading: resource present (no download) vs. missing (download triggered)
   - Test exception wrapping: Evidently failure → `RuntimeError` with chained exception
2. Create `tests/unit/monitoring/test_protocol_conformance.py`:
   - Verify `isinstance(EvidentlyQualityMonitor(), IModelMonitor)` returns `True`

**Estimated Effort:** 3 days

---

### MON-GAP-002: No Reference Data Support (Drift Detection Impossible)

**Source:** [quality.py:L101](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/monitoring/quality.py#L101)

```python
reference_data=None,  # No baseline; simple profiling run
```

**Impact:** Critical for publication. The comment explicitly acknowledges that no baseline/reference data is used. Without reference data, Evidently cannot compute **data drift** — the primary use case for model monitoring. The current implementation only performs profiling (descriptive statistics), which is far less valuable for production monitoring.

**Drift Detection Theory:**

When reference data $D_{ref}$ is provided, Evidently can compute statistical drift metrics:

| Drift Metric | Test | Null Hypothesis | Output |
|:---|:---|:---|:---|
| Population Stability Index (PSI) | Distribution comparison | $P_{ref} = P_{cur}$ | PSI value (>0.2 = significant drift) |
| Kolmogorov-Smirnov Test | Distribution shape | $F_{ref} = F_{cur}$ | p-value, KS statistic |
| Kullback-Leibler Divergence | Information loss | $D_{KL}(P_{ref} \| P_{cur}) = 0$ | KL value in nats |
| Jensen-Shannon Divergence | Symmetric divergence | $JSD(P_{ref}, P_{cur}) = 0$ | JSD value in [0, 1] |

**Without reference data, none of these metrics can be computed**, reducing the module to a descriptive profiling tool.

**Recommendation:**
1. Add `reference_data: Optional[pd.DataFrame] = None` parameter to `generate_report`
2. Update `IModelMonitor` protocol to accept optional reference data
3. When reference data is provided, Evidently computes drift scores (PSI, KS test, etc.)
4. Document the drift detection capability in the paper

**Estimated Effort:** 2-3 days

---

## Moderate Gaps

### MON-GAP-003: Protocol Imports pandas

**Source:** [model_monitor_protocol.py:L3](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/monitoring/model_monitor_protocol.py#L3)

```python
import pandas as pd  # ← Implementation dependency in interface
```

**Impact:** The `IModelMonitor` Protocol depends on `pandas.DataFrame` in its method signature. This couples the interface to a specific data library. Alternative implementations using Polars, Arrow, or raw dicts would still need to import pandas just for typing.

**Clean Architecture Violation Analysis:**

```
Protocol Layer (should be dependency-free)
    ↓ VIOLATES
pandas (external library)
```

| Framework | Protocol Type Dependency | Clean Architecture Compliance |
|:---|:---|:---|
| `IDataVersionControl` | `Path` (stdlib) | ✅ No external deps |
| `IExperimentTracker` | `Dict`, `Any`, `str` (stdlib) | ✅ No external deps |
| `IModelMonitor` | `pd.DataFrame` (**pandas**) | ❌ External dep in interface |

**Recommendation:**
1. Option A: Accept `Any` type with runtime validation in implementation
2. Option B: Define a custom `DataTable` Protocol that both pandas and Polars satisfy
3. Option C: Accept the coupling and document it as a pragmatic design decision

**Estimated Effort:** 1 day

---

### MON-GAP-004: No Numerical/Tabular Data Monitoring

**Source:** [quality.py:L96](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/monitoring/quality.py#L96)

```python
report = Report(metrics=[TextEvals()])  # ← Only text metrics
```

**Impact:** The implementation only supports text quality evaluation. No support for numerical features (model prediction drift, feature distributions, class balance). This limits the module to LLM/NLP use cases only.

**Evidently Preset Coverage Analysis:**

| Evidently Preset | Supported | Use Case | Priority |
|:---|:---|:---|:---|
| `TextEvals` | ✅ Current | LLM/NLP output quality | — |
| `DataDriftPreset` | ❌ Missing | Feature drift detection | High |
| `DataQualityPreset` | ❌ Missing | Data quality profiling | Medium |
| `ClassificationPreset` | ❌ Missing | Classification model evaluation | Medium |
| `RegressionPreset` | ❌ Missing | Regression model evaluation | Low |
| `TargetDriftPreset` | ❌ Missing | Target variable drift | Medium |

**Recommendation:**
1. Add `DataDriftPreset` for numerical feature monitoring
2. Add `ClassificationPreset` for classification model monitoring
3. Make the preset configurable via a parameter or configuration

**Estimated Effort:** 2 days

---

### MON-GAP-005: Non-Configurable Metric Selection

**Source:** [quality.py:L96](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/monitoring/quality.py#L96)

**Impact:** `TextEvals()` is hardcoded with no ability to select specific text metrics (e.g., only sentiment, or only OOV ratio). Users cannot customize the evaluation without modifying source code.

**Desired Configurability:**
```python
# Current (hardcoded)
report = Report(metrics=[TextEvals()])

# Desired (configurable)
report = Report(metrics=user_metrics or [TextEvals()])
```

**Recommendation:** Accept `metrics: Optional[List] = None` parameter; default to `[TextEvals()]` if not provided.

**Estimated Effort:** 1 day

---

### MON-GAP-006: No Threshold-Based Alerting

**Source:** The module generates HTML reports but provides no mechanism for programmatic metric extraction or threshold-based alerting.

**Impact:** In production ML monitoring, automated alerts are essential. The current implementation requires a human to open and visually inspect the HTML report, which is not scalable.

**Production Monitoring Requirements:**

| Capability | Current | Required for Production |
|:---|:---|:---|
| Metric computation | ✅ Via Evidently | ✅ |
| Visual report | ✅ HTML output | ✅ |
| Programmatic access | ❌ No dict/JSON output | ✅ Needed for CI/CD pipelines |
| Alert thresholds | ❌ None | ✅ Needed for automated monitoring |
| Historical comparison | ❌ No storage | ⚠️ Nice to have |

**Recommendation:**
1. Add `get_metrics() -> Dict[str, float]` for programmatic access
2. Add `check_thresholds(thresholds: Dict[str, float]) -> Dict[str, bool]` for alerting
3. Return both report path and metrics from `generate_report`

**Estimated Effort:** 1-2 days

---

## Minor Gaps

### MON-GAP-007: Legacy Import Path for ColumnMapping

**Source:** [quality.py:L10](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/monitoring/quality.py#L10)

```python
from evidently.legacy.pipeline.column_mapping import ColumnMapping
```

**Impact:** Uses a `legacy` import path. This may break in future Evidently versions when legacy compatibility is removed.

**Migration Path:**
```diff
-from evidently.legacy.pipeline.column_mapping import ColumnMapping
+from evidently import ColumnMapping
```

**Recommendation:** Update to `from evidently import ColumnMapping` (modern API).

**Estimated Effort:** 0.5 days

---

### MON-GAP-008: HTML-Only Report Output

**Source:** [quality.py:L104](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/monitoring/quality.py#L104)

```python
report.save_html(output_path)  # ← Only HTML format
```

**Impact:** No JSON or dict export. Programmatic consumption of report results (e.g., threshold-based alerts) requires parsing HTML, which is fragile.

**Format Comparison:**

| Format | Human-Readable | Machine-Readable | Size | Evidently Support |
|:---|:---|:---|:---|:---|
| HTML | ✅ Rich visualizations | ❌ Requires parsing | Large | `save_html()` |
| JSON | ⚠️ Structured text | ✅ Direct parsing | Medium | `json()` |
| Dict | ❌ Python-only | ✅ Native access | Small | `as_dict()` |

**Recommendation:** Add `format: str = "html"` parameter supporting `"html"`, `"json"`, and `"dict"`.

**Estimated Effort:** 1 day

---

### MON-GAP-009: No Data Sampling for Large DataFrames

**Source:** The entire DataFrame is passed to Evidently without any sampling or batching.

**Impact:** For large LLM log DataFrames (100K+ rows), the NLP analysis will be extremely slow and memory-intensive. VADER sentiment analysis and OOV detection are $O(N \cdot L)$ operations that don't scale well without sampling.

**Scalability Analysis:**

| Dataset Size | Estimated Time | Memory Usage | Practical? |
|:---|:---|:---|:---|
| 1K rows | <5 seconds | ~10 MB | ✅ |
| 10K rows | ~30 seconds | ~100 MB | ✅ |
| 100K rows | ~5 minutes | ~1 GB | ⚠️ |
| 1M rows | ~50 minutes | ~10 GB | ❌ |

**Recommendation:**
1. Add optional `sample_size: Optional[int] = None` parameter
2. Use stratified sampling to preserve distribution characteristics
3. Document the sampling strategy and its impact on metric accuracy

**Estimated Effort:** 1 day

---

### MON-GAP-010: Single-Method Protocol

**Source:** [model_monitor_protocol.py:L7-L28](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/monitoring/model_monitor_protocol.py#L7-L28)

**Impact:** The `IModelMonitor` protocol has only 1 method (`generate_report`). Compared to `IExperimentTracker` (11 methods) and `IDataVersionControl` (5 methods), this is too narrow to demonstrate the full power of Protocol-based abstraction. Reviewers may argue a simple function would suffice.

**Protocol Depth Comparison:**

| Protocol | Module | Method Count | Surface Area |
|:---|:---|:---|:---|
| `IExperimentTracker` | observability | 11 | Rich interface |
| `IDataVersionControl` | data_versioning | 5 | Moderate interface |
| `IModelMonitor` | monitoring | 1 | Minimal interface |

**Recommendation:**
1. Add `get_drift_score() -> Optional[float]` for programmatic drift queries
2. Add `configure(metrics: List, thresholds: Dict) -> None` for runtime configuration
3. Add `get_metrics_summary() -> Dict` for structured output

**Estimated Effort:** 1-2 days

---

## Gap Prioritization Matrix

| Priority | Gap IDs | Rationale | Total Effort |
|:---|:---|:---|:---|
| **P0 (Blocks publication)** | MON-GAP-001, MON-GAP-002 | No tests + core feature missing | 5-6 days |
| **P1 (Weakens paper)** | MON-GAP-003, MON-GAP-004, MON-GAP-005, MON-GAP-010 | Architecture consistency + feature depth | 5-6 days |
| **P2 (Production concern)** | MON-GAP-006, MON-GAP-009 | Alerting + scalability | 2-3 days |
| **P3 (Enhancement)** | MON-GAP-007, MON-GAP-008 | Maintenance + format flexibility | 1.5 days |
| **Total** | | | **13.5-16.5 days** |
