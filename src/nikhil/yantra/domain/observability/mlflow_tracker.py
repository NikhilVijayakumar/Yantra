# src/nikhil/yantra/domain/observability/service/mlflow_tracker.py
import contextlib

import mlflow
from typing import Any, Dict, Optional, ContextManager

import pandas as pd
from yantra.domain.observability import IExperimentTracker


class MLflowTracker(IExperimentTracker):
    def __init__(self, tracking_uri: str, experiment_name: str):
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)

    def enable_system_metrics(self) -> None:
        # This starts a background thread to monitor CPU/RAM/GPU
        mlflow.enable_system_metrics_logging()

    def log_dataset(self, dataset_source: Any, context: str = "input", name: Optional[str] = None):
        """
        Wraps mlflow.log_input.
        If dataset_source is a DataFrame, we convert it to an MLflow dataset.
        """
        try:
            # Assuming dataset_source is a Pandas DataFrame
            if isinstance(dataset_source, pd.DataFrame):
                dataset = mlflow.data.from_pandas(dataset_source, name=name)
                mlflow.log_input(dataset, context=context)
            else:
                # Fallback or specific logic for other types if needed
                print(f"Warning: log_dataset received non-DataFrame type: {type(dataset_source)}")
        except Exception as e:
            print(f"Failed to log dataset: {e}")

    def autolog_crewai(self) -> None:
        mlflow.crewai.autolog()

    def autolog_gemini(self) -> None:
        mlflow.gemini.autolog(log_traces=True, disable=False)

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

    @contextlib.contextmanager
    def start_span(self, name: str, inputs: Optional[Dict] = None):
        """
        Starts an MLflow span and optionally sets its inputs.
        """
        with mlflow.start_span(name=name) as span:
            if inputs:
                span.set_inputs(inputs)
            yield span

    def end_run(self):
        mlflow.end_run()