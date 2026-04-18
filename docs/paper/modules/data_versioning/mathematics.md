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

### Idempotency Proof Sketch

Define the system state $\Sigma = \{B_{absent}, B_{exists}, B_{forbidden}\}$. The state transitions under `ensure_bucket` form an absorbing Markov chain:

$$
\begin{aligned}
\delta(B_{absent}) &= B_{exists} \quad &\text{(create\_bucket succeeds)} \\
\delta(B_{exists}) &= B_{exists} \quad &\text{(no-op, already exists)} \\
\delta(B_{forbidden}) &= \bot \quad &\text{(exception, no state change)}
\end{aligned}
$$

Since $B_{exists}$ is an **absorbing state** ($\delta(B_{exists}) = B_{exists}$), repeated application is guaranteed to be idempotent:

$$
\forall k \geq 1: \quad \delta^k(B_{absent}) = \delta^1(B_{absent}) = B_{exists}
$$

This satisfies the mathematical definition of idempotence: $f \circ f = f$.

### Variable Mapping

| LaTeX Symbol | Code Variable | Type | Location |
|:---|:---|:---|:---|
| $B$ | `bucket_name` | `str` | `dvc_setup.py:L56` |
| $\sigma$ | `error_code` | `str` | `dvc_setup.py:L72` |
| S3 client | `s3_client` | `boto3.client` | `dvc_setup.py:L58` |
| Endpoint | `endpoint_url` | `str` | `dvc_setup.py:L60` |
| $\Sigma$ | System states | Set | Conceptual |

### Complexity Analysis

- **Time:** $O(1)$ — single HTTP HEAD request + conditional create
- **Space:** $O(1)$ — no persistent in-memory state
- **Network:** 1-2 round-trips (HEAD always, CREATE conditionally)

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

### State Transition Model

The sync workflow can be modeled as a **finite state machine** $M = (Q, \Sigma, \delta, q_0, F)$:

$$
Q = \{q_{start}, q_{pulled}, q_{tracked}, q_{checked}, q_{committed}, q_{pushed}, q_{error}\}
$$

$$
\delta: Q \times \Sigma \to Q
$$

| Current State | Event | Next State | Action |
|:---|:---|:---|:---|
| $q_{start}$ | `sync()` | $q_{pulled}$ | `dvc pull` |
| $q_{pulled}$ | success | $q_{tracked}$ | `dvc add` (input + output) |
| $q_{tracked}$ | success | $q_{checked}$ | `git status --porcelain` |
| $q_{checked}$ | `.dvc` found | $q_{committed}$ | `git add + commit` |
| $q_{checked}$ | no `.dvc` | $q_{pushed}$ | Skip commit |
| $q_{committed}$ | success | $q_{pushed}$ | `dvc push` |
| $q_{pushed}$ | success | $q_{start}$ | Complete |
| Any | error | $q_{error}$ | Raise `YantraDVCError` |

The accepting state is $F = \{q_{pushed}\}$, and $q_{error}$ is a trap state.

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
- **Subprocess calls:** 5-7 per sync (pull + 2×add + status + conditional add/commit + push)

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

### Null Object Pattern Analysis

The defensive track implements a variant of the **Null Object Pattern** at the filesystem level:

$$
\text{sentinel}(p) = p / \texttt{.gitkeep} \quad \text{(zero-byte file)}
$$

This ensures the invariant:

$$
\text{pre: } \neg\text{exists}(p) \implies \text{post: exists}(p) \wedge |p| \geq 1
$$

Where $|p|$ denotes the file count in directory $p$. This guards against DVC's `dvc add` failing on empty directories (DVC requires at least one file to generate a `.dvc` metadata file).

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

### Pipeline Reliability Model

Assuming independent failure probabilities for each stage:

$$
P(\text{setup success}) = \prod_{i=1}^{4} (1 - p_{fail,i})
$$

Where the individual stage failure modes are:

| Stage | Component | Failure Modes | $p_{fail}$ Estimate |
|:---|:---|:---|:---|
| 1 | `create_dirs` | Disk full, permissions | Very low |
| 2 | `ensure_bucket` | Network, auth, S3 unavailable | Moderate |
| 3 | `configure_dvc` | DVC not installed, permission | Low |
| 4 | `bootstrap_data` | Network, DVC error, Git error | Moderate |

The fail-fast semantics mean no wasted computation on downstream stages when an upstream stage fails:

$$
\text{cost}(\text{failure at stage } i) = \sum_{j=1}^{i} \text{cost}(stage_j) \quad \text{vs.} \quad \sum_{j=1}^{4} \text{cost}(stage_j)
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

---

## Algorithm 5: Content-Addressable Storage via DVC Hashing

**Source:** Implicit in DVC CLI operations — [dvc_tracker.py:L66](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/data_versioning/dvc_tracker.py#L66), [dvc_setup.py:L121-L122](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/data_versioning/dvc_setup.py#L121-L122)

### Description

When `dvc add` is invoked, DVC internally computes an MD5 hash of each tracked file/directory and stores the mapping in a `.dvc` metadata file. This implements a **content-addressable storage (CAS)** scheme where data is identified by its content hash rather than by file name or timestamp.

### Formal Representation

Let $\mathcal{F} = \{f_1, f_2, \ldots, f_n\}$ be the set of files in a tracked directory $d$:

$$
H(d) = \text{MD5}\left(\bigoplus_{i=1}^{n} \text{MD5}(f_i)\right)
$$

Where $\bigoplus$ denotes hash aggregation (sorted concatenation of individual file hashes).

The resulting `.dvc` metadata file stores:

$$
\text{meta}(d) = \langle H(d), |d|, \text{nfiles}(d), \text{remote\_url} \rangle
$$

### Content-Addressable Lookup

Data retrieval via `dvc pull` is a hash-based lookup:

$$
\text{pull}(H) = \text{S3.GET}(\text{remote\_url} / H[:2] / H[2:])
$$

DVC uses the first 2 characters of the hash as a directory prefix (similar to Git's object storage), giving $O(1)$ amortized lookup:

$$
\text{storage\_path}(H) = \frac{H}{16^2} \text{ directories} \times \frac{N}{256} \text{ files/dir}
$$

This ensures uniform distribution across 256 subdirectories, preventing filesystem hotspots.

### Deduplication Property

Content-addressable storage provides automatic deduplication:

$$
f_a = f_b \implies H(f_a) = H(f_b) \implies \text{stored\_once}(f_a, f_b)
$$

For a dataset with duplication ratio $r$:

$$
\text{storage\_savings} = 1 - \frac{|\text{unique}(\mathcal{F})|}{|\mathcal{F}|} = 1 - (1 - r)
$$

### Variable Mapping

| LaTeX Symbol | Code Variable | Type | Location |
|:---|:---|:---|:---|
| $d$ | Directory being tracked | `Path` | `dvc_tracker.py:L66` |
| $H(d)$ | `.dvc` file content (md5 field) | `str` | Generated by DVC CLI |
| `.dvc` metadata | `*.dvc` files | YAML | Git-tracked |
| S3 path | `s3://{bucket}/dvc_store/{hash}` | `str` | `dvc_setup.py:L95` |

### Complexity Analysis

- **Time:** $O(S)$ where $S$ = total bytes across all files (MD5 computation is $O(n)$ in message length)
- **Space:** $O(n)$ — one hash (128-bit) per file, plus metadata YAML

---

## Algorithm 6: Conditional Git Commit with Timestamp Fingerprinting

**Source:** [dvc_tracker.py:L82-L89](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/data_versioning/dvc_tracker.py#L82-L89)

### Description

The `sync` method performs a **conditional Git commit** that only triggers when DVC metadata files have changed. It uses Git's porcelain status format to detect `.dvc` file modifications and appends a timestamp to the commit message for auditability.

### Formal Representation

Let $G$ be the git working tree status and $\Delta_{dvc}$ be the set of changed `.dvc` files:

$$
\Delta_{dvc} = \{f \in G \mid f \text{ matches } \texttt{"*.dvc"}\}
$$

$$
\text{commit}_{cond}(\Delta_{dvc}) =
\begin{cases}
\text{git\_add}(\texttt{"*.dvc"}, \texttt{".gitignore"}) \to \text{git\_commit}(m \| t) & \text{if } |\Delta_{dvc}| > 0 \\
\text{no-op} & \text{if } |\Delta_{dvc}| = 0
\end{cases}
$$

Where $t = \text{datetime.now}().\text{strftime}(\texttt{"\%Y-\%m-\%d \%H:\%M"})$.

The timestamp fingerprinting creates a total order on data versions:

$$
v_i \prec v_j \iff t_i < t_j
$$

This enables chronological auditing of data changes through `git log` on `.dvc` files.

### Variable Mapping

| LaTeX Symbol | Code Variable | Type | Location |
|:---|:---|:---|:---|
| $G$ | `status.stdout` | `str` | `dvc_tracker.py:L83` |
| $\Delta_{dvc}$ | `.dvc` in status | detection | `dvc_tracker.py:L84` |
| $m$ | `self.commit_msg` | `str` | `dvc_tracker.py:L25` |
| $t$ | `ts` | `str` | `dvc_tracker.py:L88` |

### Complexity Analysis

- **Time:** $O(|\text{working tree}|)$ — `git status` scans the working tree
- **Space:** $O(1)$ — status output is parsed in memory

---

## Cross-Algorithm Dependency Graph

The 6 algorithms form a directed acyclic graph (DAG) of dependencies:

$$
\text{setup}() \to \{A_1, A_4\} \to \{A_3, A_5\} \to \{A_2, A_6\}
$$

| Algorithm | Depends On | Called By |
|:---|:---|:---|
| A1 (Idempotent Provisioning) | None | A4 (Bootstrap) |
| A2 (Sync Workflow) | A3, A5, A6 | Client code |
| A3 (Defensive Track) | A5 | A2 (Sync), A4 (Bootstrap) |
| A4 (Bootstrap) | A1, A3, A5 | `setup()` |
| A5 (CAS Hashing) | None (DVC internal) | A3, A4 |
| A6 (Conditional Commit) | None | A2 (Sync) |
