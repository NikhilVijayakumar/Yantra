# Data Versioning Module - Architecture

## Figure 1: Class Diagram — Protocol-Based Data Versioning Layer

*Caption: Class hierarchy showing the `IDataVersionControl` protocol (5 methods, `@runtime_checkable`), the `DVCSetup` infrastructure provisioner, and the `DVCDataTracker` workflow executor. Separation of concerns between setup (infrastructure) and tracking (workflow) is clearly delineated. All names verified against source code.*

```mermaid
classDiagram
    class IDataVersionControl {
        <<Protocol>>
        <<runtime_checkable>>
        +setup() None
        +track(path: Path) None
        +pull() None
        +push() None
        +sync() None
    }

    class DVCSetup {
        -config_path: Path
        -config: dict
        -root_dir: Path
        -input_dir: Path
        -output_dir: Path
        -s3_config: dict
        +__init__(config_path: str)
        -_run_command(command: list, check: bool) CompletedProcess
        -_create_directories() None
        -_ensure_bucket_exists() None
        -_configure_dvc() None
        -_bootstrap_data() None
        +setup() None
    }

    class DVCDataTracker {
        -config_path: Path
        -config: dict
        -root_dir: Path
        -input_dir: Path
        -output_dir: Path
        -commit_msg: str
        +__init__(config_path: str)
        -_run_command(command: list, check: bool) CompletedProcess
        +setup() None
        +pull() None
        +track(path: Path) None
        +push() None
        +sync() None
    }

    class YantraDVCError {
        <<exception>>
    }

    IDataVersionControl <|.. DVCDataTracker : implements
    DVCDataTracker ..> DVCSetup : delegates setup to
    DVCSetup ..> YantraDVCError : raises
    DVCDataTracker ..> YantraDVCError : raises

    note for IDataVersionControl "Source: data_version_protocol.py:L7-L28"
    note for DVCSetup "Source: dvc_setup.py:L18-L148"
    note for DVCDataTracker "Source: dvc_tracker.py:L10-L91"
```

---

## Figure 2: Sequence Diagram — `sync()` Full Workflow

*Caption: Sequence diagram showing the complete `DVCDataTracker.sync()` workflow: Pull → Track(input) → Track(output) → conditional Git Commit → DVC Push. Verified against `dvc_tracker.py:L72-L91`.*

```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant Tracker as DVCDataTracker
    participant DVC as DVC CLI
    participant Git as Git CLI
    participant S3 as S3/MinIO Remote

    Client->>Tracker: sync()

    Note over Tracker,DVC: Stage 1: Pull
    Tracker->>DVC: dvc pull
    DVC->>S3: Fetch latest data
    S3-->>DVC: Data files
    DVC-->>Tracker: OK

    Note over Tracker,DVC: Stage 2: Track
    Tracker->>Tracker: track(input_dir)
    alt input_dir missing
        Tracker->>Tracker: mkdir + .gitkeep
    end
    Tracker->>DVC: dvc add input_dir
    DVC-->>Tracker: OK

    Tracker->>Tracker: track(output_dir)
    Tracker->>DVC: dvc add output_dir
    DVC-->>Tracker: OK

    Note over Tracker,Git: Stage 3: Conditional Commit
    Tracker->>Git: git status --porcelain
    Git-->>Tracker: status output

    alt ".dvc" in status
        Tracker->>Git: git add *.dvc .gitignore
        Tracker->>Git: git commit -m "msg (timestamp)"
        Git-->>Tracker: Committed
    else No DVC changes
        Note over Tracker: Skip commit
    end

    Note over Tracker,S3: Stage 4: Push
    Tracker->>DVC: dvc push
    DVC->>S3: Upload tracked data
    S3-->>DVC: OK
    Tracker-->>Client: Sync complete
```

---

## Figure 3: Sequence Diagram — `DVCSetup.setup()` Infrastructure Bootstrap

*Caption: Sequence diagram showing the 4-stage infrastructure bootstrap: directory creation, S3 bucket provisioning (with idempotent create), DVC remote configuration, and initial data bootstrapping. Verified against `dvc_setup.py:L133-L148`.*

```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant Setup as DVCSetup
    participant FS as File System
    participant S3 as S3/MinIO
    participant DVC as DVC CLI
    participant Git as Git CLI

    Client->>Setup: setup()

    Note over Setup,FS: Stage 1: Create Directories
    Setup->>FS: mkdir(input_dir)
    Setup->>FS: mkdir(output_dir)

    Note over Setup,S3: Stage 2: Ensure Bucket
    Setup->>S3: head_bucket(bucket_name)
    alt 200 OK
        S3-->>Setup: Bucket exists
    else 404 Not Found
        Setup->>S3: create_bucket(bucket_name)
        S3-->>Setup: Created
    else 403 Forbidden
        Setup--xClient: YantraDVCError
    end

    Note over Setup,DVC: Stage 3: Configure DVC
    Setup->>DVC: dvc init (if no .dvc dir)
    Setup->>DVC: dvc remote add -d s3_storage s3://bucket/dvc_store
    Setup->>DVC: dvc remote modify endpointurl
    Setup->>DVC: dvc remote modify --local access_key_id
    Setup->>DVC: dvc remote modify --local secret_access_key

    Note over Setup,S3: Stage 4: Bootstrap Data
    Setup->>DVC: dvc pull (check=False)
    Setup->>DVC: dvc add input_dir
    Setup->>DVC: dvc add output_dir
    Setup->>Git: git add + git commit
    Setup->>DVC: dvc push
    Setup-->>Client: DVC Environment Ready
```

---

## Figure 4: Component Diagram — Module Dependencies

*Caption: Component-level view showing internal structure and external dependencies. The module bridges DVC CLI, Git CLI, boto3, and YAML configuration. Verified via `import` statements.*

```mermaid
flowchart TD
    subgraph "Data Versioning Module"
        direction TB
        PROTO["IDataVersionControl\n(Protocol)"]
        SETUP["DVCSetup\n(Infrastructure)"]
        TRACK["DVCDataTracker\n(Workflow)"]
        ERR["YantraDVCError\n(Exception)"]
    end

    subgraph "External Dependencies"
        direction TB
        DVC["DVC CLI\n(subprocess)"]
        GIT["Git CLI\n(subprocess)"]
        BOTO["boto3\n(S3 client)"]
        YAML["YamlUtils\n(yantra.utils)"]
    end

    subgraph "Configuration"
        direction TB
        CFG["srotas.yaml\n(config file)"]
    end

    TRACK -->|implements| PROTO
    TRACK -->|delegates setup to| SETUP
    SETUP -->|provisions bucket via| BOTO
    SETUP -->|configures via| DVC
    SETUP -->|commits via| GIT
    TRACK -->|tracks via| DVC
    TRACK -->|commits via| GIT
    SETUP -->|loads| YAML
    TRACK -->|loads| YAML
    YAML -->|reads| CFG
    SETUP -->|raises| ERR
    TRACK -->|raises| ERR
```

---

## Table 1: Protocol Method Coverage

*Caption: Complete enumeration of `IDataVersionControl` protocol methods and their implementation in `DVCDataTracker`. Source: `data_version_protocol.py:L7-L28`, `dvc_tracker.py:L10-L91`.*

| S.No | Method | Protocol (L#) | Implementation (L#) | Underlying Commands |
|:---:|:---|:---|:---|:---|
| 1 | `setup()` | L10 | L38-L45 | Delegates to `DVCSetup.setup()` |
| 2 | `track(path)` | L14 | L55-L66 | `mkdir`, `touch .gitkeep`, `dvc add` |
| 3 | `pull()` | L18 | L47-L53 | `dvc pull` (with `.dvc` existence check) |
| 4 | `push()` | L22 | L68-L70 | `dvc push` |
| 5 | `sync()` | L26 | L72-L91 | `pull` → `track` × 2 → `git commit` → `push` |

---

## Table 2: DVC CLI Commands Used

*Caption: All DVC and Git CLI commands invoked via `subprocess.run()`, their purpose, and source location.*

| S.No | Command | Purpose | Source | Error Handling |
|:---:|:---|:---|:---|:---|
| 1 | `dvc init` | Initialize DVC repo | `dvc_setup.py:L91` | Conditional (if `.dvc` missing) |
| 2 | `dvc remote add -d` | Set default remote | `dvc_setup.py:L98` | `--force` flag |
| 3 | `dvc remote modify` | Configure remote settings | `dvc_setup.py:L103-L111` | `check=True` |
| 4 | `dvc pull` | Download from remote | `dvc_tracker.py:L53` | `check=False` (tolerant) |
| 5 | `dvc add` | Track files/directories | `dvc_tracker.py:L66` | `check=True` |
| 6 | `dvc push` | Upload to remote | `dvc_tracker.py:L70` | `check=True` |
| 7 | `git status --porcelain` | Check for changes | `dvc_tracker.py:L83` | `check=True` |
| 8 | `git add` | Stage DVC metadata | `dvc_tracker.py:L86` | `check=True` |
| 9 | `git commit` | Commit with timestamp | `dvc_tracker.py:L89` | `check=True` |
