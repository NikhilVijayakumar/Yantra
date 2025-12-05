from typing import Protocol, Optional, runtime_checkable


@runtime_checkable
class IKeyProvider(Protocol):
    """Provides API keys or credentials for remote LLMs when required."""


    def get_key(self, model_name: str) -> Optional[str]: # pragma: no cover - protocol
        ...