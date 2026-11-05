from typing import Dict, List, Optional, Any
from app.config import settings
from app.providers.base import LLMProvider, ModelInfo, CompletionResponse
from app.providers.ollama import OllamaProvider
from app.providers.lm_studio import LMStudioProvider
from app.providers.llamacpp import LlamaCppProvider
from app.providers.openai_compatible import OpenAICompatibleProvider

class ProviderManager:
    def __init__(self):
        self.providers: Dict[str, LLMProvider] = {
            "ollama": OllamaProvider(settings.OLLAMA_BASE_URL),
            "lm_studio": LMStudioProvider(settings.LM_STUDIO_BASE_URL),
            "llamacpp": LlamaCppProvider(settings.LLAMACPP_BASE_URL),
            "openai_compatible": OpenAICompatibleProvider(settings.GENERIC_OPENAI_BASE_URL),
        }

    def get_provider(self, name: Optional[str] = None) -> LLMProvider:
        provider_name = name or settings.DEFAULT_PROVIDER
        if provider_name not in self.providers:
            # Fall back to first available or default
            return self.providers.get("ollama") or list(self.providers.values())[0]
        return self.providers[provider_name]

    def update_provider_url(self, name: str, base_url: str) -> None:
        if name == "ollama":
            self.providers[name] = OllamaProvider(base_url)
        elif name == "lm_studio":
            self.providers[name] = LMStudioProvider(base_url)
        elif name == "llamacpp":
            self.providers[name] = LlamaCppProvider(base_url)
        elif name == "openai_compatible":
            self.providers[name] = OpenAICompatibleProvider(base_url)

    async def detect_available_providers(self) -> Dict[str, Dict[str, Any]]:
        status = {}
        for name, provider in self.providers.items():
            is_up = await provider.is_available()
            models = []
            if is_up:
                try:
                    models = await provider.list_models()
                except Exception:
                    pass
            status[name] = {
                "available": is_up,
                "base_url": provider.base_url,
                "models": [m.model_dump() for m in models],
            }
        return status

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None,
        response_format: Optional[str] = None,
    ) -> CompletionResponse:
        provider = self.get_provider(provider_name)
        # Fast 1.5s connectivity check to prevent stalling on offline or unreachable local servers
        is_up = await provider.is_available()
        if not is_up:
            raise ConnectionError(f"Local provider '{provider.name}' is offline or not responding at {provider.base_url}")

        model = model_name or settings.DEFAULT_MODEL
        temp = temperature if temperature is not None else settings.TEMPERATURE
        tp = top_p if top_p is not None else settings.TOP_P
        tokens = max_tokens if max_tokens is not None else settings.MAX_TOKENS
        to = timeout if timeout is not None else settings.LLM_TIMEOUT

        return await provider.generate(
            messages=messages,
            model=model,
            temperature=temp,
            top_p=tp,
            max_tokens=tokens,
            timeout=to,
            response_format=response_format,
        )

provider_manager = ProviderManager()

