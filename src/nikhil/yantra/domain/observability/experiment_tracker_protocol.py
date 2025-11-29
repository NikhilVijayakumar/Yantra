# src/nikhil/yantra/domain/observability/experiment_tracker_protocol.py
from typing import Protocol, Any, Dict, Optional, List, ContextManager

import mlflow


class IExperimentTracker(Protocol):
    """Protocol for logging experiments with Modern GenAI support."""

    def start_run(self, run_name: str, nested: bool = False) -> Any: ...

    def log_metric(self, key: str, value: float, step: Optional[int] = None) -> None: ...

    def log_param(self, key: str, value: Any) -> None: ...

    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None) -> None: ...

    def log_llm_trace(self, name: str, inputs: Dict[str, Any], outputs: Dict[str, Any],
                      metadata: Optional[Dict] = None) -> None:
        """
        Log a trace for an LLM interaction.
        Compatible with MLflow Tracing (v2.14+).
        """
        ...

    def start_span(self, name: str, inputs: Optional[Dict] = None) -> Any:
        """Start a trace span for complex chains (e.g., RAG retrieval step)."""
        ...

    def end_run(self) -> None: ...

    def autolog_crewai(self)-> None: ...

    def autolog_gemini(self) -> None: ...

