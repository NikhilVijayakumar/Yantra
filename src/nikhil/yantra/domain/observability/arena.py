# src/nikhil/yantra/domain/observability/arena.py
import mlflow
import pandas as pd


class ModelArena:
    """Helper to compare multiple models on the same dataset."""

    def compare_models(self,
                       eval_data: pd.DataFrame,
                       models: list[Any],
                       prompts_column: str = "question"):
        results = []
        for model in models:
            with mlflow.start_run(run_name=f"eval_{model.name}"):
                # 1. Run Inference
                predictions = model.predict(eval_data[prompts_column])

                # 2. Log Results to MLflow
                mlflow.log_param("model_name", model.name)

                # 3. Use MLflow's native evaluator to compare
                evaluation = mlflow.evaluate(
                    model=model.uri,  # or python_function
                    data=eval_data,
                    targets="ground_truth",  # optional
                    model_type="text",
                )
                results.append(evaluation)
        return results