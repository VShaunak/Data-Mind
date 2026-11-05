from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str
    size: Optional[str] = None
    context_length: Optional[int] = 8192
    modified_at: Optional[str] = None

class CompletionResponse(BaseModel):
    content: str
    model: str
    provider: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None
    latency_ms: Optional[float] = None

class LLMProvider(ABC):
    """Abstract base class for all local and remote LLM providers."""
    name: str
    base_url: str

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the provider server is running and accessible."""
        pass

    @abstractmethod
    async def list_models(self) -> List[ModelInfo]:
        """Fetch list of available models from this provider."""
        pass

    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.1,
        top_p: float = 0.95,
        max_tokens: int = 4096,
        timeout: int = 120,
        response_format: Optional[str] = None,
    ) -> CompletionResponse:
        """Execute chat completion request."""
        pass

    @abstractmethod
    async def test_connection(self, model: str) -> Dict[str, Any]:
        """Run a test query to verify responsiveness."""
        pass

