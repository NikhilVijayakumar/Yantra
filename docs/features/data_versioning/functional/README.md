# Data Versioning Module - Functional Documentation

## Overview
The **Data Versioning** module brings Version Control to your datasets, ensuring that your data is as reproducible as your code. It wraps **DVC (Data Version Control)** and **AWS S3/MinIO** to provide a seamless workflow for tracking, pulling, and pushing large datasets.

## Capabilities

### 1. Automated Setup (`setup`)
-   **One-Click Initialization:** Automatically initializes DVC, creates S3 buckets, configures remotes, and handles authentication.
-   **Directory Management:** Ensures local input/output directories exist before processing.

### 2. Data Synchronization (`sync`)
-   **Unified Workflow:** A single command (`sync`) handles the entire data lifecycle:
    1.  **Pull:** Fetch latest data from S3.
    2.  **Track:** Add new local data to DVC.
    3.  **Commit:** Git commit the `.dvc` files.
    4.  **Push:** Upload changes to S3.

### 3. S3/MinIO Integration
-   **Cloud Native:** Designed to work with S3-compatible storage (AWS S3, MinIO).
-   **Smart Bucket Handling:** Automatically detects invalid bucket states (404, 403) and attempts repairs (creation) where possible.

## Usage

### Basic Workflow
```python
from yantra.domain.data_versioning import DVCDataTracker

# 1. Initialize with config
tracker = DVCDataTracker(config_path="config/dvc_config.yaml")

# 2. First-time setup (run once)
tracker.setup()

# 3. Daily Workflow
# This will Pull -> Add -> Commit -> Push automatically
tracker.sync()
```

### Manual Control
You can also run individual steps:
```python
tracker.pull()  # Get latest data
# ... modify data in data/input ...
tracker.track() # Add changes
tracker.push()  # Upload to S3
```
