# Monitoring Module - Mathematical Logic

## Algorithm 1: Lazy NLTK Resource Acquisition

**Source:** [quality.py:L39-L55](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/monitoring/quality.py#L39-L55)

### Description

The `EvidentlyQualityMonitor` implements a **lazy initialization** pattern for NLTK resources. On construction, it iterates over a fixed set of required corpora and lexicons, checks whether each exists locally, and downloads only those that are missing. This prevents redundant downloads in Docker/CI environments while ensuring first-run correctness.

### Formal Representation

Let $\mathcal{R} = \{(c_1, p_1), (c_2, p_2), \ldots, (c_n, p_n)\}$ be the set of required NLTK resources, where $c_i$ is the check path and $p_i$ is the package name.

The resource acquisition function $\text{ensure}$ is:

$$
\text{ensure}(\mathcal{R}) = \bigcup_{i=1}^{n} \text{acquire}(c_i, p_i)
$$

Where:

$$
\text{acquire}(c_i, p_i) =
\begin{cases}
\emptyset & \text{if } \texttt{nltk.data.find}(c_i) \text{ succeeds (resource cached)} \\
\texttt{nltk.download}(p_i) & \text{if } \texttt{LookupError} \text{ is raised (resource missing)}
\end{cases}
$$

### Variable Mapping

| LaTeX Symbol | Code Variable | Type | Location |
|:---|:---|:---|:---|
| $\mathcal{R}$ | `NLTK_REQUIREMENTS` | `List[Tuple[str, str]]` | `quality.py:L26-L31` |
| $c_i$ | `check_path` | `str` | `quality.py:L39` |
| $p_i$ | `pkg_name` | `str` | `quality.py:L39` |
| $n$ | `len(NLTK_REQUIREMENTS)` | `int` = 4 | `quality.py:L26` |

### Complexity Analysis

- **Time (cold start):** $O(n \cdot D)$ — where $D$ is the download time per resource (network-bound)
- **Time (warm):** $O(n)$ — each `nltk.data.find()` is a local filesystem check
- **Space:** $O(1)$ — no additional in-memory state; resources stored on disk

---

## Algorithm 2: Text Quality Report Generation Pipeline

**Source:** [quality.py:L60-L112](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/monitoring/quality.py#L60-L112)

### Description

The `generate_report` method implements a 4-stage pipeline: (1) input validation, (2) column mapping construction, (3) Evidently report execution with TextEvals preset, and (4) HTML serialization. The method takes a DataFrame of LLM logs, runs NLP-based quality evaluations (sentiment, text length, OOV ratio, etc.), and produces a self-contained HTML report.

### Formal Representation

Given a DataFrame $D$ with $N$ rows and a target text column $t$:

$$
\text{generate\_report}(D, t, p) =
\begin{cases}
\text{error} & \text{if } t \notin \text{columns}(D) \\
\text{save\_html}\Big(\text{Evidently.run}(D, \mathcal{M}_{text}), p\Big) & \text{otherwise}
\end{cases}
$$

Where:
- $\mathcal{M}_{text} = \texttt{TextEvals()}$ is the preset containing NLP metrics
- $p$ is the output file path

The TextEvals preset internally computes:

$$
\mathcal{M}_{text}(D, t) = \Big\{\mu_{sent}(D_t), \; \mu_{len}(D_t), \; \mu_{oov}(D_t), \; \mu_{words}(D_t) \Big\}
$$

Where:
- $\mu_{sent}(D_t) = \frac{1}{N} \sum_{i=1}^{N} \text{VADER}(D_t^{(i)})$ — mean sentiment score
- $\mu_{len}(D_t) = \frac{1}{N} \sum_{i=1}^{N} |D_t^{(i)}|$ — mean character length
- $\mu_{oov}(D_t) = \frac{1}{N} \sum_{i=1}^{N} \frac{|\text{OOV}(D_t^{(i)})|}{|\text{tokens}(D_t^{(i)})|}$ — mean out-of-vocabulary ratio
- $\mu_{words}(D_t) = \frac{1}{N} \sum_{i=1}^{N} |\text{tokens}(D_t^{(i)})|$ — mean word count

### Variable Mapping

| LaTeX Symbol | Code Variable | Type | Location |
|:---|:---|:---|:---|
| $D$ | `df_logs` | `pd.DataFrame` | `quality.py:L62` |
| $t$ | `text_column` | `str` | `quality.py:L64` |
| $p$ | `output_path` | `str` | `quality.py:L63` |
| $\mathcal{M}_{text}$ | `TextEvals()` | `Report Preset` | `quality.py:L96` |
| $N$ | `len(df_logs)` | `int` | implicit |
| $D_t^{(i)}$ | `df_logs[text_column].iloc[i]` | `str` | implicit |

### Complexity Analysis

- **Time:** $O(N \cdot L)$ — where $N$ is the number of rows and $L$ is the average text length (NLP metrics are linear in text length)
- **Space:** $O(N \cdot |\mathcal{M}|)$ — stores metric results for each row × each metric

---

## Algorithm 3: Column Validation with Diagnostic Error

**Source:** [quality.py:L79-L84](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/monitoring/quality.py#L79-L84)

### Description

Before executing the expensive Evidently pipeline, the method performs a **fail-fast validation** that checks whether the target text column exists in the input DataFrame. If missing, it raises a `ValueError` with diagnostic information including all available column names.

### Formal Representation

$$
\text{validate}(D, t) =
\begin{cases}
\bot \text{ (raise ValueError with columns}(D)) & \text{if } t \notin \text{columns}(D) \\
\top \text{ (proceed)} & \text{if } t \in \text{columns}(D)
\end{cases}
$$

### Variable Mapping

| LaTeX Symbol | Code Variable | Type | Location |
|:---|:---|:---|:---|
| $D$ | `df_logs` | `pd.DataFrame` | `quality.py:L62` |
| $t$ | `text_column` | `str` | `quality.py:L64` |
| $\text{columns}(D)$ | `df_logs.columns` | `Index` | `quality.py:L80` |

### Complexity Analysis

- **Time:** $O(c)$ — where $c$ is the number of columns (membership check)
- **Space:** $O(c)$ — for the error message containing column names
