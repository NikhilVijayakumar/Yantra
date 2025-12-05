import json
import logging
from typing import Dict, Any

from evidently.descriptors import LLMJudge

from yantra.domain.monitoring.model_judge_protocol import IModelJudge

logger = logging.getLogger(__name__)

class EvidentlyJudgeAdapter(LLMJudge):
    """
    Adapter that implements Evidently's LLMJudge interface by delegating to
    an IModelJudge. This keeps Yantra model-agnostic.
    """

    def __init__(self, judge: IModelJudge, rules: Dict[str, Any], timeout_seconds: int = 30):
        # Evidently's LLMJudge might not take arguments in __init__ in some versions,
        # but we need to store our judge and rules.
        # If LLMJudge is a Pydantic model (likely in 0.7.17), we should be careful.
        # Assuming it's a mixin or base class we can subclass.
        super().__init__()
        self._judge = judge
        self._rules = rules
        self._timeout = timeout_seconds

    def _call_model(self, prompt: str) -> str:
        """
        Evidently calls this method with the prompt constructed from the template.
        We delegate to our judge.
        """
        try:
            # Delegate to the judge; expect a dict
            result = self._judge.judge(prompt, self._rules)
            # Ensure serializable JSON string for Evidently
            return json.dumps(result)
        except Exception as e:
            logger.error(f"Judge evaluation failed: {e}")
            # Return a fallback JSON so Evidently doesn't crash
            return json.dumps({"score": 0.0, "explanation": f"Evaluation failed: {str(e)}"})