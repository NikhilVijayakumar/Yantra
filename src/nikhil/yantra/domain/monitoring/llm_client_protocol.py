from typing import Protocol, runtime_checkable


@runtime_checkable
class ILlmClient(Protocol):
    """
    Abstraction for an LLM client used to generate judge responses.


    Implementations must adapt to their provider (Gemini/OpenAI/LMStudio/etc.)
    and return the textual output for a given prompt.
    """


    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generates a response for the given prompt.

        Args:
            prompt: The input prompt for the LLM.
            **kwargs: Additional arguments for the LLM (e.g., temperature, max_tokens).

        Returns:
            The generated text response.
        """
        ...