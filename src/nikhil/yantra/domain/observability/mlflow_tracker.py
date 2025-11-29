# src/nikhil/yantra/domain/observability/service/mlflow_tracker.py
import mlflow
from typing import Any, Dict, Optional, ContextManager

from yantra.domain.observability import IExperimentTracker


class MLflowTracker(IExperimentTracker):
    def __init__(self, tracking_uri: str, experiment_name: str):
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        mlflow.gemini.autolog(log_traces=True, disable=False)
        # mlflow.openai.autolog()

    def start_run(self, run_name: str, nested: bool = False) -> Any:
        return mlflow.start_run(run_name=run_name, nested=nested)

    def log_metric(self, key: str, value: float, step: Optional[int] = None):
        mlflow.log_metric(key, value, step=step)

    def log_param(self, key: str, value: Any):
        mlflow.log_param(key, value)

    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None):
        mlflow.log_artifact(local_path, artifact_path)

    def log_llm_trace(self, name: str, inputs: Dict[str, Any], outputs: Dict[str, Any],
                      metadata: Optional[Dict] = None):
        """
        Logs a trace to the MLflow 'Traces' tab.
        Compatible with MLflow 2.14+.
        """
        # CORRECTED LINE: Use the top-level function
        root_span = mlflow.get_current_active_span()

        if root_span:
            # If we are already inside a trace (e.g., inside a @mlflow.trace function),
            # just add attributes/events to the current span.
            root_span.set_attributes(metadata or {})
            # Note: We don't overwrite outputs of a parent span usually,
            # but we can log an event or a child span if needed.
            with mlflow.start_span(name=name) as child_span:
                child_span.set_inputs(inputs)
                child_span.set_outputs(outputs)
                child_span.set_attributes(metadata or {})
        else:
            # If no active trace exists, start a NEW trace hierarchy.
            # mlflow.start_span() automatically creates a new Trace if none exists.
            with mlflow.start_span(name=name) as span:
                span.set_inputs(inputs)
                span.set_outputs(outputs)
                span.set_attributes(metadata or {})

    def start_span(self, name: str, inputs: Optional[Dict] = None) -> ContextManager:
        return mlflow.start_span(name=name, inputs=inputs)

    def end_run(self):
        mlflow.end_run()