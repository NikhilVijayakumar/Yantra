# Application Execution Results — User Input Template

> **Purpose:** This template is pre-filled with suggested metrics, baselines, and experiment structures inferred from Yantra's module analyses. Fill in actual empirical values where indicated with `___`. Mark experiments you have completed with ✅ and those pending with ⬜.

---

## 1. Protocol Overhead Benchmarks

*Derived from: `observability/novelty.md` (Gap 1), `cross_module/novelty.md` (Section 4)*

### Experiment 1.1: Protocol Abstraction Overhead

**Hypothesis:** Protocol-based method dispatch adds negligible overhead (< 1%) compared to direct SDK calls.

| Metric | Direct SDK Call | Via Protocol | Overhead (%) | Status |
|:---|:---:|:---:|:---:|:---:|
| `mlflow.log_metric()` (1000 calls, avg ms) | ___ | ___ | ___% | ⬜ |
| `mlflow.start_span()` (100 calls, avg ms) | ___ | ___ | ___% | ⬜ |
| `mlflow.log_artifact()` (10 calls, avg ms) | ___ | ___ | ___% | ⬜ |
| `evidently.Report.run()` (10 calls, avg ms) | ___ | ___ | ___% | ⬜ |
| `subprocess("dvc push")` (5 calls, avg ms) | ___ | ___ | ___% | ⬜ |

**Setup:**
- Python version: ___
- MLflow version: ___
- Machine specs: ___
- Repetitions per measurement: ___

### Experiment 1.2: Decorator Overhead — `@yantra_task`

*Derived from: `orchestration/mathematics.md` (Algorithm 1, 6)*

**Hypothesis:** The dual-context decorator adds < 5ms overhead per call beyond standard Prefect task execution.

| Metric | Raw Prefect `@task` | `@yantra_task` (with tracker) | `@yantra_task` (no tracker — degraded) | Status |
|:---|:---:|:---:|:---:|:---:|
| Empty function (avg ms) | ___ | ___ | ___ | ⬜ |
| Function with 5 params (avg ms) | ___ | ___ | ___ | ⬜ |
| Function with 20 params (avg ms) | ___ | ___ | ___ | ⬜ |
| Memory per invocation (KB) | ___ | ___ | ___ | ⬜ |

**Expected overhead sources:**
- `inspect.signature().bind()` — $O(p)$ where $p$ = parameter count
- `YantraContext.get_tracker()` — $O(1)$ class attribute access
- `str(result)[:1000]` — $O(L)$ truncation

---

## 2. Module-Specific Execution Results

### 2.1 Observability: ModelArena Evaluation

*Derived from: `observability/novelty.md` (Contribution 2)*

**Suggested benchmarks against alternatives:**

| Framework | Setup Time (min) | Evaluation Time (100 prompts, s) | Metrics Captured | Lines of Code |
|:---|:---:|:---:|:---:|:---:|
| **Yantra ModelArena** | ___ | ___ | 3 (sim, rel, tox) | ~15 |
| **RAGAS** | ___ | ___ | ___ | ___ |
| **DeepEval** | ___ | ___ | ___ | ___ |
| **LangChain Evaluate** | ___ | ___ | ___ | ___ |

**Arena execution results (if available):**

| Model Name | Similarity Score (1-5) | Relevance Score (1-5) | Toxicity Score (0-1) | Overall Rank |
|:---|:---:|:---:|:---:|:---:|
| ___ | ___ | ___ | ___ | ___ |
| ___ | ___ | ___ | ___ | ___ |
| ___ | ___ | ___ | ___ | ___ |

### 2.2 Monitoring: Quality Report Generation

*Derived from: `monitoring/novelty.md` (Contribution 3), `monitoring/mathematics.md`*

| Metric | Value | Status |
|:---|:---:|:---:|
| Report generation time (1K rows, ms) | ___ | ⬜ |
| Report generation time (10K rows, ms) | ___ | ⬜ |
| Report generation time (100K rows, ms) | ___ | ⬜ |
| NLTK cold start (first run, ms) | ___ | ⬜ |
| NLTK warm start (cached, ms) | ___ | ⬜ |
| NLTK warm/cold speedup factor | ___× | ⬜ |
| VADER sentiment accuracy on LLM text | ___% | ⬜ |
| OOV ratio for typical LLM output | ___% | ⬜ |

**Expected:** NLTK warm/cold speedup ≈ 1000× (from `monitoring/novelty.md`)

### 2.3 Data Versioning: Sync Overhead

*Derived from: `data_versioning/novelty.md` (Gap 2)*

| Dataset Size | Manual CLI (5 commands, s) | `sync()` (1 call, s) | Overhead (%) | Status |
|:---|:---:|:---:|:---:|:---:|
| 1 MB | ___ | ___ | ___% | ⬜ |
| 100 MB | ___ | ___ | ___% | ⬜ |
| 1 GB | ___ | ___ | ___% | ⬜ |

**Idempotency validation:**

| Test | Expected | Actual | Status |
|:---|:---|:---:|:---:|
| `setup()` called 1× → state S1 | Infrastructure created | ___ | ⬜ |
| `setup()` called 2× → state S2 | S2 == S1 (idempotent) | ___ | ⬜ |
| `pull()` on unchanged data | No-op (hash match) | ___ | ⬜ |
| `sync()` with no changes | No Git commit created | ___ | ⬜ |

---

## 3. System-Level Integration Tests

*Derived from: `cross_module/interactions.md` (Section 6), `cross_module/gaps.md` (SYS-GAP-002)*

### Experiment 3.1: End-to-End Pipeline

**Suggested test: Run all 4 modules in a single MLOps pipeline.**

| Step | Module | Operation | Result | Status |
|:---|:---|:---|:---:|:---:|
| 1 | data_versioning | `sync()` — pull latest data | ___ | ⬜ |
| 2 | orchestration | `@yantra_task(preprocess)` | ___ | ⬜ |
| 3 | orchestration | `@yantra_task(train_model)` | ___ | ⬜ |
| 4 | monitoring | `generate_report(results_df)` | ___ | ⬜ |
| 5 | observability | `log_artifact(report_path)` | ___ | ⬜ |
| 6 | data_versioning | `push()` — version output | ___ | ⬜ |

### Experiment 3.2: Retry-Trace Audit

**Suggested test: Verify that Prefect retries create distinct MLflow spans.**

| Scenario | Retries | Expected Spans | Actual Spans | Final Status | Status |
|:---|:---:|:---:|:---:|:---:|:---:|
| Success on 1st try | 0 | 1 | ___ | success | ⬜ |
| Fail 1×, succeed 2nd | 1 | 2 | ___ | success | ⬜ |
| Fail 3×, succeed 4th | 3 | 4 | ___ | success | ⬜ |
| Fail all retries | 3 | 4 | ___ | error | ⬜ |

---

## 4. Test Coverage Results

*Derived from: `cross_module/gaps.md` (SYS-GAP-001)*

| Module | Source LOC | Test LOC | Line Coverage (%) | Branch Coverage (%) | Status |
|:---|:---:|:---:|:---:|:---:|:---:|
| `observability` | 210 | ___ | ___% | ___% | ⬜ |
| `orchestration` | 96 | ___ | ___% | ___% | ⬜ |
| `monitoring` | 146 | ___ | ___% | ___% | ⬜ |
| `data_versioning` | 280 | ___ | ___% | ___% | ⬜ |
| **Total** | **732** | ___ | ___% | ___% | |

---

## 5. Framework Comparison Summary

*Derived from: `cross_module/novelty.md` (Section 1)*

**Fill after running comparable experiments on alternative frameworks:**

| Framework | Architecture | LOC (core) | Domains | Protocol-Based | Backend Swap | Overhead (ms/call) |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **Yantra** | Protocol-first library | ~782 | 4 | ✅ | ✅ | ___ |
| **ZenML** | Pipeline-first | ~50K+ | 5+ | ❌ | ✅ | ___ |
| **Metaflow** | DAG-first | ~20K+ | 3 | ❌ | ⚠️ | ___ |
| **Kedro** | Pipeline-first | ~30K+ | 3 | ❌ | ✅ | ___ |
| **Dagster** | Graph-first | ~100K+ | 5+ | ❌ | ✅ | ___ |

---

## Instructions

1. Run each experiment marked ⬜ in your environment
2. Fill in `___` blanks with actual measured values
3. Change ⬜ to ✅ when complete
4. Add notes on any unexpected results
5. This data will feed directly into the paper's **Experimental Evaluation** section
