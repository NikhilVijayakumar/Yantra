# src/nikhil/yantra/domain/observability/service/mlflow_tracker.py
import mlflow

from nikhil.yantra.domain.observability.experiment_tracker_protocol import IExperimentTracker



class MLflowTracker(IExperimentTracker):
    def __init__(self, tracking_uri: str, experiment_name: str):
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)

    def log_llm_trace(self, prompt: str, response: str, model_name: str):
        # Use MLflow's new LLM Tracking capabilities
        mlflow.log_param("model", model_name)
        mlflow.log_text(prompt, "prompt.txt")
        mlflow.log_text(response, "response.txt")