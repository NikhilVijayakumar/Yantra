# Orchestration Module - Research Gap Analysis

## Gap Summary

| S.No | Gap ID | Severity | Description | Effort |
|:---:|:---|:---|:---|:---|
| 1 | ORC-GAP-001 | **Critical** | No unit tests for decorator or context | 3-4 days |
| 2 | ORC-GAP-002 | **Critical** | No integration test verifying Prefect + MLflow interaction | 2-3 days |
| 3 | ORC-GAP-003 | **Moderate** | YantraContext is not thread-safe | 1 day |
| 4 | ORC-GAP-004 | **Moderate** | Output truncation at 1000 chars is arbitrary | 0.5 days |
| 5 | ORC-GAP-005 | **Moderate** | No async task support | 2 days |
| 6 | ORC-GAP-006 | **Minor** | Context not exported via `__init__.py` | 0.5 days |
| 7 | ORC-GAP-007 | **Minor** | No flow-level decorator (only task-level) | 1-2 days |

---

## Critical Gaps

### ORC-GAP-001: No Unit Tests

**Source:** Verified via `find tests/ -name "*orchestration*"` — **0 results**

**Impact:** Blocks publication. The decorator contains non-trivial logic (context checking, argument binding, span management, error handling) that is completely untested. Claims about the decorator's reliability are unverifiable.

**Recommendation:**
1. Create `tests/unit/orchestration/test_yantra_task.py`:
   - Mock `prefect.task`, `prefect.get_run_logger`, and `IExperimentTracker`
   - Test with tracker present vs. absent
   - Test with successful execution vs. exception
   - Verify span attributes are set correctly
   - Verify argument binding works with various signatures (positional, keyword, defaults)
2. Create `tests/unit/orchestration/test_context.py`:
   - Test singleton behavior of `YantraContext`
   - Test `set_tracker` / `get_tracker` lifecycle
   - Test default state is `None`

**Estimated Effort:** 3-4 days

---

### ORC-GAP-002: No Integration Test for Dual-Context Bridge

**Source:** The entire value proposition of this module is the Prefect + MLflow bridge, but this is never tested end-to-end.

**Impact:** Critical for publication. The paper claims "seamless integration between Prefect orchestration and MLflow observability," but without a test demonstrating both systems working together, this claim is unsupported.

**Recommendation:**
1. Create `tests/e2e/orchestration/test_prefect_mlflow_bridge.py`:
   - Start a real Prefect flow with 2-3 `@yantra_task` functions
   - Use `MLflowTracker` with a local tracking URI
   - Verify Prefect ran the tasks successfully
   - Verify MLflow recorded the spans with correct inputs/outputs
   - Measure timing overhead of the decoration

**Estimated Effort:** 2-3 days

---

## Moderate Gaps

### ORC-GAP-003: YantraContext is Not Thread-Safe

**Source:** [context.py:L12](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/orchestration/context.py#L12)

```python
_tracker: Optional[IExperimentTracker] = None  # ← Class-level mutable state
```

**Impact:** In multi-threaded Prefect deployments, concurrent tasks could read/write `_tracker` simultaneously, causing race conditions. Prefect's `ConcurrentTaskRunner` uses threads by default.

**Recommendation:**
1. Use `threading.Lock` to protect `set_tracker` / `get_tracker`
2. Or use `contextvars.ContextVar` for proper async/thread isolation:
   ```python
   import contextvars
   _tracker_var: contextvars.ContextVar[Optional[IExperimentTracker]] = contextvars.ContextVar('_tracker', default=None)
   ```
3. Document the concurrency model in the paper

**Estimated Effort:** 1 day

---

### ORC-GAP-004: Arbitrary Output Truncation

**Source:** [prefect_utils.py:L56](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/orchestration/prefect_utils.py#L56)

```python
span.set_outputs({"result": str(result)[:1000]})  # ← Magic number 1000
```

**Impact:** The truncation limit of 1000 characters is hardcoded without rationale. For large DataFrames or complex objects, this may either be too much (performance) or too little (information loss). The code comment acknowledges this concern but offers no solution.

**Recommendation:**
1. Make truncation configurable via decorator parameter: `output_max_chars: int = 1000`
2. Add smart truncation: detect `pd.DataFrame` and log `.shape` instead of `str()`
3. Document the trade-off in the paper

**Estimated Effort:** 0.5 days

---

### ORC-GAP-005: No Async Task Support

**Source:** [prefect_utils.py:L30](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/orchestration/prefect_utils.py#L30)

```python
def wrapper(*args, **kwargs):  # ← synchronous only
```

**Impact:** Prefect supports `async def` tasks natively. The current decorator only wraps synchronous functions. Async tasks (e.g., async API calls, async database queries) cannot use `@yantra_task`.

**Recommendation:**
1. Add `inspect.iscoroutinefunction(func)` check in decorator
2. If async, create an `async def wrapper` variant
3. Use `async with tracker.start_span(...)` for async span management

**Estimated Effort:** 2 days

---

## Minor Gaps

### ORC-GAP-006: YantraContext Not Exported via `__init__.py`

**Source:** [__init__.py:L3-L5](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/orchestration/__init__.py#L3-L5)

```python
from .prefect_utils import yantra_task

__all__ = ['yantra_task']  # ← YantraContext not exported
```

**Impact:** Consumers must import `YantraContext` via the internal path `yantra.domain.orchestration.context` instead of the public API. This breaks the module's encapsulation principles.

**Recommendation:** Add `YantraContext` to `__all__` and import it in `__init__.py`.

**Estimated Effort:** 0.5 days

---

### ORC-GAP-007: No Flow-Level Decorator

**Source:** The module only provides `@yantra_task` (task-level). No equivalent `@yantra_flow` decorator exists for top-level Prefect flows.

**Impact:** Users must manually configure MLflow context at the flow level, reducing the "zero-configuration" benefit.

**Recommendation:** Create `@yantra_flow` that sets up `YantraContext` and wraps `prefect.flow()` with an MLflow parent run.

**Estimated Effort:** 1-2 days
