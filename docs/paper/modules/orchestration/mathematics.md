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

The execution of $f'$ follows:

$$
f'(\mathbf{x}) =
\begin{cases}
f(\mathbf{x}) & \text{if } \tau = \emptyset \text{ (no tracker)} \\
\text{span}\Big(f(\mathbf{x}), \; \sigma_{in}=\text{bind}(f, \mathbf{x}), \; \sigma_{out}=\text{truncate}(y, 1000)\Big) & \text{if } \tau \neq \emptyset
\end{cases}
$$

Where:
- $\tau = \texttt{YantraContext.get\_tracker()}$
- $\text{bind}(f, \mathbf{x}) = \texttt{inspect.signature}(f).\texttt{bind}(\mathbf{x}).\texttt{arguments}$
- $y = f(\mathbf{x})$ is the return value
- $\text{truncate}(y, 1000) = \texttt{str}(y)[:1000]$

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

The `YantraContext` class implements a Singleton-style context that holds the active experiment tracker. This eliminates the need to pass tracker instances through every function call in the pipeline.

### Formal Representation

Let $\mathcal{C}$ be the application context and $\tau$ be a tracker instance:

$$
\text{set}: \mathcal{C} \times \tau \rightarrow \mathcal{C}' \quad \text{where } \mathcal{C}'._\text{tracker} = \tau
$$

$$
\text{get}: \mathcal{C} \rightarrow \tau \cup \{\emptyset\}
$$

The singleton property ensures:

$$
\forall \text{ invocations } i, j: \quad \mathcal{C}_i.\text{get\_tracker}() = \mathcal{C}_j.\text{get\_tracker}() \iff \text{set was called between } i \text{ and } j
$$

### Variable Mapping

| LaTeX Symbol | Code Variable | Type | Location |
|:---|:---|:---|:---|
| $\mathcal{C}$ | `YantraContext` | `class` | `context.py:L7` |
| $\tau$ | `_tracker` | `Optional[IExperimentTracker]` | `context.py:L12` |

### Complexity Analysis

- **Time:** $O(1)$ for both `set_tracker` and `get_tracker`
- **Space:** $O(1)$ — single class-level variable
