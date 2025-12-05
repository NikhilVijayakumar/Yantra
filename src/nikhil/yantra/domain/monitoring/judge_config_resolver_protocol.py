from typing import Protocol, Dict, Any, runtime_checkable


@runtime_checkable
class IJudgeConfigResolver(Protocol):
    """Resolves judge configuration rules based on the dataset/metadata/context."""


    def get_rules(self, context: Dict[str, Any]) -> Dict[str, Any]: # pragma: no cover - protocol
        ...