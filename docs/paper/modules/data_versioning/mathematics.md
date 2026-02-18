# Data Versioning Module - Mathematical Logic

## Algorithm 1: Idempotent S3 Bucket Provisioning

**Source:** [dvc_setup.py:L54-L83](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/data_versioning/dvc_setup.py#L54-L83)

### Description

The `_ensure_bucket_exists` method implements an **idempotent provisioning** algorithm for S3-compatible buckets (MinIO or AWS). It uses an HTTP HEAD request (`head_bucket`) to check bucket existence and conditionally creates it only when absent. Error codes are dispatched to handle authorization failures distinctly from "not found" conditions.

### Formal Representation

Let $B$ be the bucket name and $\sigma$ be the HTTP status code from `head_bucket(B)$:

$$
\text{ensure\_bucket}(B) =
\begin{cases}
\top \text{ (ready)} & \text{if } \sigma = 200 \\
\text{create\_bucket}(B) & \text{if } \sigma = 404 \\
\bot \text{ (raise YantraDVCError)} & \text{if } \sigma = 403 \\
\bot \text{ (raise YantraDVCError)} & \text{otherwise}
\end{cases}
$$

The idempotency property:

$$
\forall n \geq 1: \quad \text{ensure\_bucket}^n(B) \equiv \text{ensure\_bucket}^1(B)
$$

I.e., calling the function multiple times produces the same final state as calling it once.

### Variable Mapping

| LaTeX Symbol | Code Variable | Type | Location |
|:---|:---|:---|:---|
| $B$ | `bucket_name` | `str` | `dvc_setup.py:L56` |
| $\sigma$ | `error_code` | `str` | `dvc_setup.py:L72` |
| S3 client | `s3_client` | `boto3.client` | `dvc_setup.py:L58` |
| Endpoint | `endpoint_url` | `str` | `dvc_setup.py:L60` |

### Complexity Analysis

- **Time:** $O(1)$ — single HTTP HEAD request + conditional create
- **Space:** $O(1)$ — no persistent in-memory state

---

## Algorithm 2: DVC Sync Workflow (Pull → Track → Commit → Push)

**Source:** [dvc_tracker.py:L72-L91](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/data_versioning/dvc_tracker.py#L72-L91)

### Description

The `sync` method implements a 4-stage data synchronization workflow that orchestrates DVC and Git commands. It first pulls the latest remote data, tracks local changes in input/output directories, conditionally commits to Git if DVC metadata has changed, and pushes both DVC data and Git history.

### Formal Representation

Let $\mathcal{S}$ represent the system state (local files + remote storage):

$$
\text{sync}(\mathcal{S}_0) = \text{push} \circ \text{commit}_{cond} \circ \text{track} \circ \text{pull}(\mathcal{S}_0)
$$

Expanded:

$$
\mathcal{S}_1 = \text{pull}(\mathcal{S}_0) \quad \text{// dvc pull}
$$

$$
\mathcal{S}_2 = \text{track}(\mathcal{S}_1, d_{in}) \cup \text{track}(\mathcal{S}_1, d_{out}) \quad \text{// dvc add}
$$

$$
\mathcal{S}_3 = \begin{cases}
\text{git\_commit}(\mathcal{S}_2, m \| \text{timestamp}) & \text{if } \texttt{".dvc"} \in \text{git\_status}(\mathcal{S}_2) \\
\mathcal{S}_2 & \text{otherwise}
\end{cases}
$$

$$
\mathcal{S}_4 = \text{push}(\mathcal{S}_3) \quad \text{// dvc push}
$$

### Variable Mapping

| LaTeX Symbol | Code Variable | Type | Location |
|:---|:---|:---|:---|
| $d_{in}$ | `self.input_dir` | `Path` | `dvc_tracker.py:L23` |
| $d_{out}$ | `self.output_dir` | `Path` | `dvc_tracker.py:L24` |
| $m$ | `self.commit_msg` | `str` | `dvc_tracker.py:L25` |
| timestamp | `ts` | `str` | `dvc_tracker.py:L88` |
| git status | `status.stdout` | `str` | `dvc_tracker.py:L83` |

### Complexity Analysis

- **Time:** $O(F)$ — dominated by file I/O; $F$ = total files across input/output directories
- **Space:** $O(F)$ — DVC computes content hashes for all tracked files

---

## Algorithm 3: Defensive Track with Placeholder Creation

**Source:** [dvc_tracker.py:L55-L66](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/data_versioning/dvc_tracker.py#L55-L66)

### Description

The `track` method implements a **defensive tracking** algorithm. Before running `dvc add`, it checks whether the target directory exists. If missing, it creates the directory and places a `.gitkeep` sentinel file, preventing DVC from failing on an empty or nonexistent path.

### Formal Representation

Let $p$ be the target path and $p_{default}$ be `self.input_dir`:

$$
\text{track}(p) =
\begin{cases}
\text{dvc\_add}(p_{default}) & \text{if } p = \text{None} \\
\text{mkdir}(p) \to \text{touch}(p/\texttt{.gitkeep}) \to \text{dvc\_add}(p) & \text{if } \neg\text{exists}(p) \\
\text{dvc\_add}(p) & \text{if } \text{exists}(p)
\end{cases}
$$

### Variable Mapping

| LaTeX Symbol | Code Variable | Type | Location |
|:---|:---|:---|:---|
| $p$ | `path` | `Optional[Path]` | `dvc_tracker.py:L55` |
| $p_{default}$ | `self.input_dir` | `Path` | `dvc_tracker.py:L57` |
| Target | `target` | `Path` | `dvc_tracker.py:L57` |

### Complexity Analysis

- **Time:** $O(F_p)$ — where $F_p$ is the number of files in the target directory (DVC hashing)
- **Space:** $O(1)$ — directory creation is filesystem-only

---

## Algorithm 4: Multi-Stage DVC Infrastructure Bootstrap

**Source:** [dvc_setup.py:L133-L148](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/data_versioning/dvc_setup.py#L133-L148)

### Description

The `DVCSetup.setup` method orchestrates a 4-stage infrastructure bootstrap: (1) local directory creation, (2) S3 bucket provisioning, (3) DVC CLI configuration with remote credentials, and (4) initial data bootstrapping (pull → add → commit → push). Each stage is idempotent and wrapped in error handling.

### Formal Representation

$$
\text{setup}() = \text{bootstrap} \circ \text{configure\_dvc} \circ \text{ensure\_bucket} \circ \text{create\_dirs}
$$

The pipeline is sequential with fail-fast semantics:

$$
\forall i \in \{1,2,3,4\}: \quad \text{stage}_i \text{ executes } \iff \text{stage}_{i-1} \text{ succeeded}
$$

### Variable Mapping

| LaTeX Symbol | Code Variable | Type | Location |
|:---|:---|:---|:---|
| Stage 1 | `_create_directories()` | method | `dvc_setup.py:L47` |
| Stage 2 | `_ensure_bucket_exists()` | method | `dvc_setup.py:L54` |
| Stage 3 | `_configure_dvc()` | method | `dvc_setup.py:L85` |
| Stage 4 | `_bootstrap_data()` | method | `dvc_setup.py:L114` |

### Complexity Analysis

- **Time:** $O(N_{net} + F)$ — dominated by network calls ($N_{net}$) and file tracking ($F$)
- **Space:** $O(1)$ — all state is persisted to filesystem/S3
