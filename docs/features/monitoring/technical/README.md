# Monitoring Module - Technical Documentation

## Design Decisions

### 1. Evidently Integration for Text
We chose **Evidently AI** as the core engine for text quality monitoring.
-   **Why:** Evidently has robust, pre-built presets for NLP (`TextEvals`), offering immediate value without custom metric implementation.
-   **Implementation:** `EvidentlyQualityMonitor` wraps Evidently's `Report` API.

### 2. NLTK Resource Management
Text analysis requires NLTK corpora (e.g., `vader_lexicon`, `wordnet`).
-   **Automatic Download:** The module automatically checks for and downloads missing NLTK resources upon initialization (`_ensure_nltk_resources`).
-   **Why:** Prevents runtime crashes in new environments (CI/CD, Docker) where these data files might be missing.

### 3. Protocol-Based Interface (`IModelMonitor`)
Defined in `model_monitor_protocol.py`.
-   **Contract:** 
    ```python
    def generate_report(self, df_logs: pd.DataFrame, output_path: str, text_column: str) -> str: ...
    ```
-   **Benefit:** Decouples the monitoring logic from the specific tool. Future implementations could use `Whylogs` for privacy-preserving profiling.

## Data Flow

1.  **Input:** A pandas DataFrame containing a column of text (e.g., LLM responses).
2.  **Processing:** 
    -   `EvidentlyQualityMonitor` validates the input.
    -   It initializes an Evidently `Report` with `TextEvals` preset.
    -   Evidently calculates metrics (Statistically/Heuristically).
3.  **Output:** An HTML file is written to the specified `output_path`.

## Contracts

### `EvidentlyQualityMonitor`
-   **Input:** `pd.DataFrame`
-   **Output:** Path to HTML file (`str`)
-   **Side Effects:** Filesystem write (HTML report), NLTK data download (network request).

## Dependencies
-   `evidently`: Core monitoring engine.
-   `nltk`: Required for text processing features in Evidently.
-   `pandas`: Log data structure.
