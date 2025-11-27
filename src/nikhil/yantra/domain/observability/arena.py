# src/nikhil/yantra/domain/observability/arena.py
from typing import Any, List, Optional
import mlflow
import pandas as pd
from mlflow.metrics.genai import answer_similarity, answer_relevance
from mlflow.metrics import toxicity


class ModelArena:
    """
    Comparison framework for LLMs.
    Uses MLflow Evaluate to run 'LLM-as-a-Judge' metrics.
    """

    def __init__(self, tracker_uri: str):
        mlflow.set_tracking_uri(tracker_uri)

    def compare_models(self,
                       eval_data: pd.DataFrame,
                       model_uris: List[str],
                       run_name_prefix: str = "arena_eval",
                       prompts_column: str = "question",
                       ground_truth_column: str = "ground_truth"):
        """
        Compares registered MLflow models or generic functions.

        Args:
            eval_data: Pandas DataFrame containing questions and ground truth.
            model_uris: List of MLflow model URIs (e.g. "runs:/<id>/model")
                        OR python function wrappers.
        """
        results = []

        # Define default GenAI metrics (requires OpenAI key env var usually)
        # In production, you would configure these specifically
        eval_metrics = [
            answer_similarity(),
            answer_relevance(),
            toxicity()
        ]

        for uri in model_uris:
            # Extract a friendly name from the URI
            model_name = uri.split("/")[-1] if isinstance(uri, str) else str(uri)

            run_name = f"{run_name_prefix}_{model_name}"

            print(f"⚔️ Evaluating model: {model_name}...")

            with mlflow.start_run(run_name=run_name):
                # MLflow Evaluate handles prediction AND metric calculation
                evaluation = mlflow.evaluate(
                    model=uri,
                    data=eval_data,
                    targets=ground_truth_column,
                    model_type="text",
                    evaluators=["default"],
                    extra_metrics=eval_metrics,
                    evaluator_config={"col_mapping": {"inputs": prompts_column}}
                )

                results.append({
                    "model": model_name,
                    "metrics": evaluation.metrics,
                    "artifacts": evaluation.artifacts
                })

        return pd.DataFrame([
            {"model": r["model"], **r["metrics"]} for r in results
        ])