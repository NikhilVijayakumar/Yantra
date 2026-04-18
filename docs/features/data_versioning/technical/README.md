# Data Versioning Module - Technical Documentation

## Design Decisions

### 1. Wrapper around DVC CLI
The module uses `subprocess` to invoke the `dvc` command-line tool.
-   **Why:** DVC's Python API is internal and unstable. The CLI is the public contract.
-   **Abstraction:** `DVCDataTracker` hides the complexity of DVC flags and git operations.

### 2. Separation of Concerns
-   **`DVCSetup`:** Handles infrastructure (S3 buckets, `dvc init`, `dvc remote add`). This is a "heavy" operation meant to be run rarely.
-   **`DVCDataTracker`:** Handles the daily workflow (`track`, `pull`, `push`). This is lighter and safe for frequent execution.

### 3. Protocol-Based Interface (`IDataVersionControl`)
-   **Contract:** 
    ```python
    def setup(self) -> None: ...
    def sync(self) -> None: ...
    ```
-   **Benefit:** Allows mocking the entire data layer in unit tests, avoiding slow S3/DVC calls.

## Data Flow

1.  **Setup Phase:** 
    -   `boto3` checks/creates S3 bucket.
    -   `dvc init` creates `.dvc` folder.
    -   `dvc remote add` links S3 bucket.
2.  **Sync Phase:**
    -   **Pull:** `dvc pull` downloads files from S3 to local disk.
    -   **Track:** `dvc add data/input` creates `data/input.dvc`.
    -   **Git:** `git add *.dvc` -> `git commit`.
    -   **Push:** `dvc push` uploads `data/input` contents to S3.

## Configuration
Requires a YAML config file:
```yaml
domain_root_path: "data/input"
output_dir_path: "data/output"
s3_config:
  bucket_name: "my-dvc-store"
  endpoint_url: "http://localhost:9000" # Optional (for MinIO)
  access_key_id: "..."
  secret_access_key: "..."
```

## Dependencies
-   `dvc`: The Data Version Control tool (must be installed in env).
-   `boto3`: For S3 bucket management.
-   `git`: For versioning `.dvc` files.
