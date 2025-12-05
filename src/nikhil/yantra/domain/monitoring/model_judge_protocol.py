from typing import Protocol, Dict, Any, runtime_checkable


@runtime_checkable
class IModelJudge(Protocol):
    """Judge abstraction.


    A judge converts a prompt + rules into a structured JSON dict containing
    at least 'score' and optionally 'explanation' and additional metadata.
    """


    def judge(self, prompt: str, rules: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates a prompt based on provided rules.

        Args:
            prompt: The content/prompt to evaluate.
            rules: A dictionary of rules/criteria for the evaluation.

        Returns:
            A dictionary containing the evaluation result (e.g., score, explanation).
        """
        ...