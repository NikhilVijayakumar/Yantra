import json
import logging
from typing import Optional, Generator, Union, Dict, Any

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from yantra.domain.monitoring.llm_client_protocol import ILlmClient

logger = logging.getLogger(__name__)


class GeminiClient(ILlmClient):
    """
    Robust Gemini client implementation with safety handling.
    """

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash", **genai_kwargs):
        genai.configure(api_key=api_key)
        self.model_name = model
        # Default safety settings to avoid blocking harmless eval requests
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        self.genai_kwargs = genai_kwargs
        self._model = genai.GenerativeModel(model_name=self.model_name)

    def _extract_text(self, response) -> str:
        """Safe extraction handling blocked content."""
        try:
            # Check if blocked by safety filters
            if hasattr(response, "prompt_feedback") and response.prompt_feedback:
                if response.prompt_feedback.block_reason:
                    logger.warning(f"Response blocked: {response.prompt_feedback}")
                    return json.dumps({"score": 0.0, "explanation": "Blocked by Safety Filter"})

            if hasattr(response, "text"):
                return response.text

            if hasattr(response, "candidates") and response.candidates:
                return response.candidates[0].content.parts[0].text

            return ""
        except Exception as e:
            logger.error(f"Error extracting text from Gemini response: {e}")
            return ""

    def generate(self, prompt: str, **kwargs) -> str:
        params = {**self.genai_kwargs, **kwargs}
        try:
            response = self._model.generate_content(
                prompt,
                safety_settings=self.safety_settings,
                **params
            )
            return self._extract_text(response)
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            # Fail gracefully so the pipeline doesn't crash on one row
            return json.dumps({"score": 0.0, "explanation": f"API Error: {str(e)}"})