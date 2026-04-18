# Orchestration Module - Mathematical Logic

## Algorithm 1: Dual-Context Task Decoration

**Source:** [prefect_utils.py:L9-L70](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/orchestration/prefect_utils.py#L9-L70)

### Description

The `yantra_task` decorator implements a **dual-context wrapping** algorithm. It takes an arbitrary Python function $f$ and returns a new function $f'$ that is simultaneously:
1. A **Prefect Task** (with retry configuration)
2. An **MLflow-traced function** (with automatic span creation)

The decorator uses `inspect.signature` to introspect the function signature at runtime, binds positional and keyword arguments to their parameter names, and passes this structured input to the MLflow span.

### Formal Representation

Let $f: \mathbb{X} \rightarrow \mathbb{Y}$ be the original function, and let $\mathcal{D}$ be the decorator factory.

The decoration transforms $f$ into $f'$:

$$
f' = \mathcal{D}(n, r, d, l)(f) = \text{prefect.task}(n, r, d, l) \circ \text{mlflow\_span\_wrap}(f)
$$

Where:
- $n$ is the task name (`name: str`)
- $r$ is the retry count (`retries: int = 3`)
- $d$ is the retry delay (`retry_delay_seconds: int = 5`)
- $l$ is the log flag (`log_prints: bool = True`)

### Decorator Composition Model

The dual wrapping creates a **3-layer function stack**:

$$
\text{call}(f'(\mathbf{x})) = \underbrace{\text{Prefect}}_{\text{Layer 1}} \Big( \underbrace{\text{MLflow Span}}_{\text{Layer 2}} \Big( \underbrace{f(\mathbf{x})}_{\text{Layer 3}} \Big) \Big)
$$

Layer responsibilities:

| Layer | Component | Responsibility | Failure Handling |
|:---|:---|:---|:---|
| 1 (Outer) | Prefect Task | Retry logic, scheduling, DAG | Retries $r$ times with delay $d$ |
| 2 (Middle) | MLflow Span | Tracing, input/output logging | Sets error attributes, re-raises |
| 3 (Inner) | Original Function | Business logic | Raises original exception |

### Execution State Machine

The execution follows a conditional state machine:

$$
f'(\mathbf{x}) =
\begin{cases}
f(\mathbf{x}) & \text{if } \tau = \emptyset \text{ (no tracker — graceful degradation)} \\
\text{span}\Big(f(\mathbf{x}), \; \sigma_{in}=\text{bind}(f, \mathbf{x}), \; \sigma_{out}=\text{truncate}(y, 1000)\Big) & \text{if } \tau \neq \emptyset \text{ (success)} \\
\text{span}\Big(\bot, \; \text{status}=\text{"error"}, \; \text{msg}=\text{str}(e)\Big) \to \text{raise}(e) & \text{if } \tau \neq \emptyset \text{ (failure)}
\end{cases}
$$

Where:
- $\tau = \texttt{YantraContext.get\_tracker()}$
- $\text{bind}(f, \mathbf{x}) = \texttt{inspect.signature}(f).\texttt{bind}(\mathbf{x}).\texttt{arguments}$
- $y = f(\mathbf{x})$ is the return value
- $\text{truncate}(y, 1000) = \texttt{str}(y)[:1000]$

### Retry-Trace Interaction Model

When Prefect retries a failed task, each retry creates a **new MLflow span**:

$$
\text{retry}(f', \mathbf{x}, r) = \bigcup_{i=0}^{r} \text{span}_i(f(\mathbf{x}))
$$

The final trace contains $\leq r+1$ spans for a single task, each with its own status:

$$
\text{spans}(f') = \{(\text{span}_0, \text{error}), (\text{span}_1, \text{error}), \ldots, (\text{span}_k, \text{success})\}
$$

Where $k \leq r$ is the successful retry index. This creates a complete **audit trail** of all retry attempts.

### Variable Mapping

| LaTeX Symbol | Code Variable | Type | Location |
|:---|:---|:---|:---|
| $f$ | `func` | `Callable` | `prefect_utils.py:L21` |
| $f'$ | `wrapper` | `Callable` | `prefect_utils.py:L30` |
| $n$ | `name` | `str` | `prefect_utils.py:L10` |
| $r$ | `retries` | `int` | `prefect_utils.py:L11` |
| $d$ | `retry_delay_seconds` | `int` | `prefect_utils.py:L12` |
| $\tau$ | `tracker` | `Optional[IExperimentTracker]` | `prefect_utils.py:L32` |
| $\mathbf{x}$ | `*args, **kwargs` | `Any` | `prefect_utils.py:L30` |
| $\sigma_{in}$ | `inputs` | `Dict[str, Any]` | `prefect_utils.py:L38` |
| $y$ | `result` | `Any` | `prefect_utils.py:L51` |

### Complexity Analysis

- **Time (decoration):** $O(1)$ — decorator application is constant-time function wrapping
- **Time (execution):** $O(T_f + T_{bind})$ — dominated by original function time $T_f$; `bind` is $O(p)$ where $p$ is the parameter count
- **Space:** $O(p + |\text{str}(y)|)$ — stores parameter bindings and truncated output string

---

## Algorithm 2: Signature Introspection and Argument Binding

**Source:** [prefect_utils.py:L36-L38](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/orchestration/prefect_utils.py#L36-L38)

### Description

The decorator uses Python's `inspect.signature` to dynamically introspect the decorated function's parameters. It then uses `Signature.bind()` to map positional and keyword arguments to their named parameters, and `apply_defaults()` to fill in any unspecified default values. This creates a complete dictionary of named inputs for the MLflow span.

### Formal Representation

Given function $f$ with parameters $(p_1, p_2, \ldots, p_k)$ and a call $f(a_1, a_2, \ldots, a_j, kw_1=v_1, \ldots)$:

$$
\text{bind}(f, \mathbf{A}, \mathbf{KW}) = \{p_i \mapsto v_i \mid v_i = \text{resolve}(p_i, \mathbf{A}, \mathbf{KW}, \mathbf{D})\}
$$

Where:
- $\mathbf{A} = (a_1, \ldots, a_j)$ are positional arguments
- $\mathbf{KW} = \{kw_1: v_1, \ldots\}$ are keyword arguments
- $\mathbf{D} = \{p_i: d_i\}$ are default values
- $\text{resolve}$ applies positional-first, then keyword, then default precedence

### Resolution Precedence

The binding follows a strict priority: positional args override defaults, keyword args override positional args for the same parameter:

$$
\text{resolve}(p_i) =
\begin{cases}
a_i & \text{if } p_i \text{ is matched positionally (index } i < j\text{)} \\
kw_i & \text{if } p_i \in \mathbf{KW} \\
d_i & \text{if } p_i \in \mathbf{D} \text{ (default value applied)} \\
\bot \text{ (TypeError)} & \text{otherwise (missing required param)}
\end{cases}
$$

### Binding Example

For a function `def process(data, batch_size=32, verbose=False)`:

| Call | `inputs` Dict | Notes |
|:---|:---|:---|
| `process(df)` | `{"data": df, "batch_size": 32, "verbose": False}` | Defaults applied |
| `process(df, 64)` | `{"data": df, "batch_size": 64, "verbose": False}` | Positional override |
| `process(df, verbose=True)` | `{"data": df, "batch_size": 32, "verbose": True}` | Keyword override |

### Variable Mapping

| LaTeX Symbol | Code Variable | Type | Location |
|:---|:---|:---|:---|
| $f$ | `func` | `Callable` | `prefect_utils.py:L21` |
| $\mathbf{A}$ | `*args` | `tuple` | `prefect_utils.py:L30` |
| $\mathbf{KW}$ | `**kwargs` | `dict` | `prefect_utils.py:L30` |
| `bind` result | `func_args` | `BoundArguments` | `prefect_utils.py:L36` |
| Final dict | `inputs` | `Dict[str, Any]` | `prefect_utils.py:L38` |

### Complexity Analysis

- **Time:** $O(p)$ — where $p$ is the number of parameters in the function signature
- **Space:** $O(p)$ — dictionary of parameter-value pairs

---

## Algorithm 3: Singleton Context Pattern for Tracker Injection

**Source:** [context.py:L7-L20](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/orchestration/context.py#L7-L20)

### Description

The `YantraContext` class implements a Singleton-style context that holds the active experiment tracker. It uses **class-level state** with `@classmethod` accessors, providing a global dependency injection (DI) container without requiring instance creation.

### Formal Representation

Let $\mathcal{C}$ be the application context and $\tau$ be a tracker instance:

$$
\text{set}: \mathcal{C} \times \tau \rightarrow \mathcal{C}' \quad \text{where } \mathcal{C}'._\text{tracker} = \tau
$$

$$
\text{get}: \mathcal{C} \rightarrow \tau \cup \{\emptyset\}
$$

### Singleton Guarantee

The class-level state ensures global singleton behavior:

$$
\forall \text{ modules } M_1, M_2: \quad M_1.\text{YantraContext}._\text{tracker} \equiv M_2.\text{YantraContext}._\text{tracker}
$$

Because Python modules are singletons, and class-level attributes are shared across all imports and references to the same class:

$$
\text{id}(\text{YantraContext}_{module\_1}) = \text{id}(\text{YantraContext}_{module\_2})
$$

### Service Locator Pattern Analysis

`YantraContext` implements the **Service Locator** pattern from Martin Fowler's enterprise patterns:

| Pattern Aspect | Service Locator | YantraContext |
|:---|:---|:---|
| Registration | `locator.register(service)` | `YantraContext.set_tracker(tracker)` |
| Lookup | `locator.get(Service)` | `YantraContext.get_tracker()` |
| Scope | Global | Global (class-level) |
| Type Safety | Generic | Typed (`IExperimentTracker`) |
| Default | Null Object | `None` |

### Thread Safety Analysis

The current implementation is **NOT thread-safe**:

$$
\text{Thread A: set\_tracker}(\tau_1) \| \text{Thread B: get\_tracker}() \implies \text{race condition}
$$

In Prefect's `ConcurrentTaskRunner`, multiple tasks run as threads. The class-level `_tracker` could be read while being written, though Python's GIL prevents actual data corruption. The semantic risk is a task seeing a stale or partially-updated tracker reference.

### Variable Mapping

| LaTeX Symbol | Code Variable | Type | Location |
|:---|:---|:---|:---|
| $\mathcal{C}$ | `YantraContext` | `class` | `context.py:L7` |
| $\tau$ | `_tracker` | `Optional[IExperimentTracker]` | `context.py:L12` |

### Complexity Analysis

- **Time:** $O(1)$ for both `set_tracker` and `get_tracker`
- **Space:** $O(1)$ — single class-level variable

---

## Algorithm 4: Output Truncation for Trace Storage

**Source:** [prefect_utils.py:L56](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/orchestration/prefect_utils.py#L56)

### Description

The decorator truncates the function's return value to 1000 characters before storing it on the MLflow span. This prevents large objects (DataFrames, model artifacts, large strings) from overwhelming the tracing storage while preserving a representative preview.

### Formal Representation

$$
\text{truncate}(y, L) = \texttt{str}(y)[:L]
$$

Where:
- $y$ is the function return value
- $L = 1000$ is the maximum character limit

### Information Loss Analysis

The truncation has the following properties:

$$
|\text{truncate}(y, L)| = \min(|\text{str}(y)|, L)
$$

$$
\text{info\_loss}(y) = \max(0, |\text{str}(y)| - L) \text{ characters}
$$

For common return types:

| Return Type | Typical `str()` Size | Truncated? | Information Preserved |
|:---|:---|:---|:---|
| `int`, `float`, `bool` | <20 chars | ❌ | 100% |
| Short `str` | <100 chars | ❌ | 100% |
| Small `dict` | <500 chars | ❌ | 100% |
| `pd.DataFrame` (10 rows) | ~2000 chars | ✅ | ~50% |
| `pd.DataFrame` (1000 rows) | ~200,000 chars | ✅ | ~0.5% |
| Large model output | Variable | ✅ | Variable |

### Variable Mapping

| LaTeX Symbol | Code Variable | Type | Location |
|:---|:---|:---|:---|
| $y$ | `result` | `Any` | `prefect_utils.py:L51` |
| $L$ | `1000` | `int` (hardcoded) | `prefect_utils.py:L56` |

### Complexity Analysis

- **Time:** $O(L)$ — bounded string operation
- **Space:** $O(L)$ — truncated copy

---

## Algorithm 5: Error-Aware Span Decoration with Re-Raise

**Source:** [prefect_utils.py:L61-L66](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/orchestration/prefect_utils.py#L61-L66)

### Description

When the wrapped function raises an exception, the decorator captures the error message, logs it to the span as structured attributes, then **re-raises** the exception to allow Prefect's retry mechanism to operate. This creates an error audit trail in MLflow while preserving Prefect's retry semantics.

### Formal Representation

$$
\text{error\_wrap}(f, \mathbf{x}, \sigma) =
\begin{cases}
(y, \sigma[\text{status} \leftarrow \text{success}]) & \text{if } f(\mathbf{x}) \text{ succeeds} \\
\sigma[\text{status} \leftarrow \text{error}, \text{msg} \leftarrow \text{str}(e)] \to \text{raise}(e) & \text{if } f(\mathbf{x}) \text{ raises } e
\end{cases}
$$

### Retry-Error Interaction

The re-raise is critical for Prefect integration:

$$
\text{Prefect.retry}(f') = \text{try}(f') \xrightarrow{\text{fail}} \text{wait}(d) \xrightarrow{\text{retry}} \text{try}(f') \quad (\text{up to } r \text{ times})
$$

If the decorator swallowed the exception (like `log_dataset` in the observability module), Prefect would see the task as "successful" and never retry. By re-raising, the decorator preserves the retry contract while adding observability:

$$
\underbrace{\text{MLflow: error logged}}_{\text{observability}} + \underbrace{\text{Prefect: exception propagated}}_{\text{orchestration}} = \text{dual-context error handling}
$$

### Variable Mapping

| LaTeX Symbol | Code Variable | Type | Location |
|:---|:---|:---|:---|
| $e$ | `e` | `Exception` | `prefect_utils.py:L61` |
| $\sigma$ | `span` | `MLflow Span` | `prefect_utils.py:L49` |

### Complexity Analysis

- **Time:** $O(|\text{str}(e)|)$ — exception serialization
- **Space:** $O(|\text{str}(e)|)$ — error message stored on span

---

## Algorithm 6: Graceful Degradation via Tracker Null-Check

**Source:** [prefect_utils.py:L42-L45](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/orchestration/prefect_utils.py#L42-L45)

### Description

Before creating an MLflow span, the decorator checks if a tracker is configured. If no tracker exists (development/testing environments), it logs a warning and executes the function as a standard Prefect task without any MLflow overhead. This implements the **Null Object pattern** for the tracker dependency.

### Formal Representation

$$
\text{degrade}(\tau, f, \mathbf{x}) =
\begin{cases}
f(\mathbf{x}) & \text{if } \tau = \texttt{None} \text{ (no tracker — skip MLflow)} \\
\text{span\_wrap}(\tau, f, \mathbf{x}) & \text{if } \tau \neq \texttt{None} \text{ (full tracing)}
\end{cases}
$$

### Overhead Analysis

In degraded mode (no tracker), the only overhead is:

$$
\text{overhead}_{degraded} = T_{\text{get\_tracker}} + T_{\text{bind}} + T_{\text{null\_check}}
$$

Where $T_{\text{get\_tracker}} \approx O(1)$ (class attribute access), $T_{\text{bind}} \approx O(p)$ (argument binding), and $T_{\text{null\_check}} \approx O(1)$. Note that argument binding still occurs even when no tracker is present — this is a minor inefficiency.

### Optimal Degradation (Suggested)

A more efficient degradation would skip argument binding:

$$
\text{degrade}_{opt}(\tau, f, \mathbf{x}) =
\begin{cases}
f(\mathbf{x}) & \text{if } \tau = \texttt{None} \text{ (skip bind + MLflow)} \\
\text{span\_wrap}(\tau, f, \mathbf{x}) & \text{otherwise}
\end{cases}
$$

### Variable Mapping

| LaTeX Symbol | Code Variable | Type | Location |
|:---|:---|:---|:---|
| $\tau$ | `tracker` | `Optional[IExperimentTracker]` | `prefect_utils.py:L32` |

### Complexity Analysis

- **Time:** $O(1)$ — null check
- **Space:** $O(0)$ — no additional allocation

---

## Cross-Algorithm Dependency Graph

The 6 algorithms form a linear execution pipeline within each decorated function call:

$$
A_3 \xrightarrow{\text{lookup}} A_6 \xrightarrow{\text{if tracker}} A_2 \xrightarrow{\text{bind}} A_1 \xrightarrow{\text{execute}} A_5 \xrightarrow{\text{on error}} A_4 \xrightarrow{\text{on success}}
$$

| Algorithm | Phase | Depends On | Called By |
|:---|:---|:---|:---|
| A1 (Dual-Context) | Execution orchestrator | A2, A3, A4, A5, A6 | Prefect engine |
| A2 (Signature Binding) | Input capture | None (`inspect` stdlib) | A1 |
| A3 (Singleton Context) | Tracker lookup | None | A1 (via A6) |
| A4 (Output Truncation) | Output capture | None | A1 (on success) |
| A5 (Error-Aware Decoration) | Error handling | None | A1 (on failure) |
| A6 (Graceful Degradation) | Feature toggle | A3 | A1 (guard clause) |
