# Data Versioning Module - Test Strategy

## Unit Test Scenarios
-   **[DVC-UT-001] Config Loading:** Verify `DVCDataTracker` raises `YantraDVCError` if config file is missing.
-   **[DVC-UT-002] Command Execution:** 
    -   Mock `subprocess.run`.
    -   Verify `track()` calls `dvc add`.
    -   Verify `push()` calls `dvc push`.
-   **[DVC-UT-003] Setup Logic:**
    -   Mock `boto3.client`.
    -   Verify `setup()` calls `create_bucket` if generic `ClientError` 404 is raised.

## E2E Test Scenarios
-   **[DVC-E2E-001] Infrastructure Setup (MinIO):**
    -   Point to a local MinIO instance.
    -   Run `setup()`.
    -   Verify bucket is created in MinIO.
    -   Verify `.dvc/config` contains the correct remote URL.
-   **[DVC-E2E-002] Full Sync Cycle:**
    -   Create a dummy file in `data/input`.
    -   Run `sync()`.
    -   Verify file exists in MinIO bucket.
    -   Delete local file.
    -   Run `pull()`.
    -   Verify file is restored.
