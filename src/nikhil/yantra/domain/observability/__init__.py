"""Observability domain for experiment tracking and MLflow integration."""

from .mlflow_tracker import MLflowTracker
from .experiment_tracker_protocol import IExperimentTracker
from .arena import ModelArena


def get_tracker(
    tracking_uri: str = "http://localhost:5000", 
    experiment_name: str = "default"
) -> IExperimentTracker:
    """
    Factory function to get an experiment tracker instance.
    
    Args:
        tracking_uri: MLflow tracking server URI (default: http://localhost:5000)
        experiment_name: Name of the experiment (default: "default")
        
    Returns:
        IExperimentTracker: Configured experiment tracker instance
        
    Example:
        >>> tracker = get_tracker()
        >>> tracker.log_llm_trace(
        ...     prompt="Hello",
        ...     response="Hi there!",
        ...     model_name="gpt-4"
        ... )
    """
    return MLflowTracker(tracking_uri, experiment_name)


__all__ = [
    'MLflowTracker',
    'IExperimentTracker', 
    'ModelArena',
    'get_tracker'
]
