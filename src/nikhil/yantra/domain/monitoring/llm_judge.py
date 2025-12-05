import json
import logging
import re
from typing import Dict, Any, Optional
from yantra.domain.monitoring.llm_client_protocol import ILlmClient
from yantra.domain.monitoring.model_judge_protocol import IModelJudge

logger = logging.getLogger(__name__)


class DefaultLlmJudge(IModelJudge):
    DEFAULT_TEMPLATE = (
        "You are an impartial evaluation judge. \n"
        "Rules:\n{rules}\n\n"
        "Task Input/Output to Evaluate:\n{prompt}\n\n"
        "Evaluate the response based strictly on the rules.\n"
        "Output valid JSON ONLY with fields: 'score' (float 0.0-1.0) and 'explanation' (string).\n"
        "JSON:"
    )

    def __init__(self, llm_client: ILlmClient, prompt_template: Optional[str] = None):
        self.llm_client = llm_client
        self.prompt_template = prompt_template or self.DEFAULT_TEMPLATE

    def _extract_json(self, text: str) -> str:
        """Finds the largest substring that looks like a JSON object."""
        try:
            # Look for the first outer curly brace and the last outer curly brace
            match = re.search(r"(\{.*\})", text, re.DOTALL)
            if match:
                return match.group(1)
            return text
        except Exception:
            return text

    def judge(self, prompt: str, rules: Dict[str, Any]) -> Dict[str, Any]:
        meta_prompt = self.prompt_template.format(
            rules=json.dumps(rules, indent=2),
            prompt=prompt
        )

        raw_output = self.llm_client.generate(meta_prompt)
        clean_output = self._extract_json(raw_output)

        try:
            result = json.loads(clean_output)
            # Normalize keys to lowercase just in case
            return {k.lower(): v for k, v in result.items()}
        except json.JSONDecodeError:
            logger.error(f"JSON Parse Error. Raw: {raw_output}")
            return {
                "score": 0.0,
                "explanation": "Failed to parse Judge output.",
                "raw": raw_output
            }