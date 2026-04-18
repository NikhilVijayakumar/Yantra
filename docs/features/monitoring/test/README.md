# Monitoring Module - Test Strategy

## Unit Test Scenarios
-   **[MON-UT-001] NLTK Resource Check:** Verify `_ensure_nltk_resources` attempts download if missing (mock `nltk.data.find`).
-   **[MON-UT-002] Input Validation:** Verify `generate_report` raises `ValueError` if `text_column` is missing from DataFrame.
-   **[MON-UT-003] Report Generation Logic:** 
    -   Mock `evidently.Report.run` and `evidently.Report.save_html`.
    -   Verify correct arguments are passed to Evidently.

## E2E Test Scenarios
-   **[MON-E2E-001] Real Report Generation:**
    -   Provide a small sample DataFrame.
    -   Run `generate_report`.
    -   Assert that the output HTML file exists and is not empty.
-   **[MON-E2E-002] Missing NLTK Scenarios:**
    -   (Containerized environment) Start with clean environment.
    -   Initialize monitor.
    -   Verify NLTK data is downloaded and accessible.
