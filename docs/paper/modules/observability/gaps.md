# Observability Module - Research Gap Analysis

## Gap Summary

| S.No | Gap ID | Severity | Description | Effort |
|:---:|:---|:---|:---|:---|
| 1 | OBS-GAP-001 | **Critical** | No unit tests for any module component | 3-4 days |
| 2 | OBS-GAP-002 | **Critical** | Protocol file imports `mlflow` (violates Clean Architecture) | 0.5 days |
| 3 | OBS-GAP-003 | **Moderate** | No baseline comparison for ModelArena | 2-3 days |
| 4 | OBS-GAP-004 | **Moderate** | No async support in IExperimentTracker | 2 days |
| 5 | OBS-GAP-005 | **Moderate** | log_dataset silently drops non-DataFrame types | 0.5 days |
| 6 | OBS-GAP-006 | **Minor** | No configurable metric selection for ModelArena | 1 day |
| 7 | OBS-GAP-007 | **Minor** | Missing type annotations on return values | 0.5 days |

---

## Critical Gaps

### OBS-GAP-001: No Unit Tests

**Source:** Verified via `find tests/ -name "*observability*"` — **0 results**

**Impact:** Blocks publication. Reviewers will question reliability of the observability layer claims without test evidence. No coverage data available for this module.

**Recommendation:**
1. Create `tests/unit/observability/test_mlflow_tracker.py` with mocked `mlflow` SDK
2. Create `tests/unit/observability/test_arena.py` with mock `mlflow.evaluate`
3. Verify `MLflowTracker` implements all `IExperimentTracker` methods (structural subtyping test)
4. Target: >90% branch coverage on `mlflow_tracker.py` and `arena.py`

**Estimated Effort:** 3-4 days

---

### OBS-GAP-002: Protocol Imports Implementation Dependency

**Source:** [experiment_tracker_protocol.py:L4](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/observability/experiment_tracker_protocol.py#L4)

```python
import mlflow  # ← This should NOT be in the protocol file
```

**Impact:** The Protocol file (`IExperimentTracker`) directly imports `mlflow`. This violates the Dependency Inversion Principle — the interface layer should have **zero** dependencies on the concrete implementation library. This weakens the "decoupled Protocol-based design" claim in the paper.

**Recommendation:**
1. Remove `import mlflow` from `experiment_tracker_protocol.py`
2. Verify the import is unused (it appears to be; the Protocol uses only `typing` constructs)
3. Document this fix as evidence of architectural integrity

**Estimated Effort:** 0.5 days (including verification)

---

## Moderate Gaps

### OBS-GAP-003: No Baseline Comparison for Arena

**Source:** [arena.py:L36-L39](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/observability/arena.py#L36-L39)

**Impact:** The `ModelArena` hardcodes 3 metrics (`answer_similarity`, `answer_relevance`, `toxicity`) with no comparison to other evaluation frameworks (e.g., LangChain's `evaluate`, DeepEval, RAGAS). Without baselines, the paper cannot claim the Arena approach is effective.

**Recommendation:**
1. Run the same evaluation dataset through LangChain Evaluate and RAGAS
2. Compare metric scores, execution time, and memory usage
3. Present as Table in the paper: "Comparison of LLM Evaluation Frameworks"

**Estimated Effort:** 2-3 days

---

### OBS-GAP-004: No Async Support

**Source:** [experiment_tracker_protocol.py:L7-L47](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/observability/experiment_tracker_protocol.py#L7-L47)

**Impact:** All protocol methods are synchronous. Modern LLM applications use `asyncio` extensively. The lack of `async def log_llm_trace(...)` limits applicability to async-first frameworks like LangGraph or FastAPI.

**Recommendation:**
1. Define `IAsyncExperimentTracker` as a parallel async Protocol
2. Implement `AsyncMLflowTracker` using `asyncio` wrappers
3. Benchmark sync vs. async tracing overhead

**Estimated Effort:** 2 days

---

### OBS-GAP-005: Silent Failure in log_dataset

**Source:** [mlflow_tracker.py:L30-L32](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/observability/mlflow_tracker.py#L30-L32)

```python
else:
    print(f"Warning: log_dataset received non-DataFrame type: {type(dataset_source)}")
```

**Impact:** Non-DataFrame inputs are silently ignored with a `print` statement. This violates structured logging practices and makes debugging difficult in production.

**Recommendation:**
1. Replace `print` with `logger.warning()`
2. Consider raising `TypeError` for unsupported types
3. Add support for numpy arrays and dictionaries

**Estimated Effort:** 0.5 days

---

## Minor Gaps

### OBS-GAP-006: Non-Configurable Arena Metrics

**Source:** [arena.py:L36-L40](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/observability/arena.py#L36-L40)

**Impact:** Metrics are hardcoded. Users cannot customize evaluation criteria without modifying source code.

**Recommendation:** Accept `extra_metrics` as a parameter in `compare_models()`.

**Estimated Effort:** 1 day

---

### OBS-GAP-007: Missing Return Type Annotations

**Source:** `mlflow_tracker.py:L45`, `mlflow_tracker.py:L48`, `arena.py:L18`

**Impact:** Several methods lack explicit return type annotations (e.g., `log_metric`, `log_param`, `compare_models`). This weakens the "type-safe Clean Architecture" claim.

**Recommendation:** Add `-> None` or `-> pd.DataFrame` annotations consistently.

**Estimated Effort:** 0.5 days
