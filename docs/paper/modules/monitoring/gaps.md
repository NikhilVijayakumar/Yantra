# Monitoring Module - Research Gap Analysis

## Gap Summary

| S.No | Gap ID | Severity | Description | Effort |
|:---:|:---|:---|:---|:---|
| 1 | MON-GAP-001 | **Critical** | No unit tests for any component | 3 days |
| 2 | MON-GAP-002 | **Critical** | No reference data support (drift detection impossible) | 2-3 days |
| 3 | MON-GAP-003 | **Moderate** | Protocol imports `pandas` (couples interface to implementation detail) | 1 day |
| 4 | MON-GAP-004 | **Moderate** | Only text metrics supported; no numerical/tabular monitoring | 2 days |
| 5 | MON-GAP-005 | **Moderate** | No configurable metric selection (TextEvals hardcoded) | 1 day |
| 6 | MON-GAP-006 | **Minor** | Uses legacy `ColumnMapping` import path | 0.5 days |
| 7 | MON-GAP-007 | **Minor** | No report format options (HTML only) | 1 day |

---

## Critical Gaps

### MON-GAP-001: No Unit Tests

**Source:** Verified via `find tests/ -name "*monitoring*" -o -name "*quality*" -o -name "*monitor*"` — **0 results**

**Impact:** Blocks publication. The core pipeline logic (validation, NLTK loading, Evidently report generation) is fully untested. Without mocked tests, there is no evidence that the code handles edge cases (empty DataFrame, missing column, NLTK download failure).

**Recommendation:**
1. Create `tests/unit/monitoring/test_quality_monitor.py`:
   - Mock `evidently.Report` and `nltk.data.find` / `nltk.download`
   - Test `generate_report` with valid inputs → verify HTML path returned
   - Test with missing `text_column` → verify `ValueError` raised with diagnostic columns
   - Test with empty DataFrame → verify behavior
   - Test NLTK lazy loading: resource present (no download) vs. missing (download triggered)
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

**Recommendation:**
1. Add `DataDriftPreset` for numerical feature monitoring
2. Add `ClassificationPreset` for classification model monitoring
3. Make the preset configurable via a parameter or configuration

**Estimated Effort:** 2 days

---

### MON-GAP-005: Non-Configurable Metric Selection

**Source:** [quality.py:L96](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/monitoring/quality.py#L96)

**Impact:** `TextEvals()` is hardcoded with no ability to select specific text metrics (e.g., only sentiment, or only OOV ratio). Users cannot customize the evaluation without modifying source code.

**Recommendation:** Accept `metrics: Optional[List] = None` parameter; default to `[TextEvals()]` if not provided.

**Estimated Effort:** 1 day

---

## Minor Gaps

### MON-GAP-006: Legacy Import Path for ColumnMapping

**Source:** [quality.py:L10](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/monitoring/quality.py#L10)

```python
from evidently.legacy.pipeline.column_mapping import ColumnMapping
```

**Impact:** Uses a `legacy` import path. This may break in future Evidently versions when legacy compatibility is removed.

**Recommendation:** Update to `from evidently import ColumnMapping` (modern API).

**Estimated Effort:** 0.5 days

---

### MON-GAP-007: HTML-Only Report Output

**Source:** [quality.py:L104](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/monitoring/quality.py#L104)

```python
report.save_html(output_path)  # ← Only HTML format
```

**Impact:** No JSON or dict export. Programmatic consumption of report results (e.g., threshold-based alerts) requires parsing HTML, which is fragile.

**Recommendation:** Add `format: str = "html"` parameter supporting `"html"`, `"json"`, and `"dict"`.

**Estimated Effort:** 1 day
