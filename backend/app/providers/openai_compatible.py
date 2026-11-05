import httpx
import time
from typing import List, Dict, Any, Optional
from app.providers.base import LLMProvider, ModelInfo, CompletionResponse

class OpenAICompatibleProvider(LLMProvider):
    name: str = "openai_compatible"

    def __init__(self, base_url: str, name: Optional[str] = None):
        super().__init__(base_url)
        if name:
            self.name = name

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                res = await client.get(f"{self.base_url}/models")
                return res.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> List[ModelInfo]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.base_url}/models")
                if res.status_code == 200:
                    data = res.json()
                    models = []
                    # Standard OpenAI format: {"data": [{"id": "...", ...}]}
                    items = data.get("data", []) if isinstance(data, dict) else []
                    for m in items:
                        model_id = m.get("id", "unknown")
                        models.append(
                            ModelInfo(
                                id=model_id,
                                name=model_id,
                                provider=self.name,
                                context_length=m.get("context_length", 8192)
                            )
                        )
                    return models
        except Exception:
            pass
        return []

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
        start_time = time.time()
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "stream": False,
        }
        if response_format == "json":
            payload["response_format"] = {"type": "json_object"}

        async with httpx.AsyncClient(timeout=float(timeout)) as client:
            res = await client.post(f"{self.base_url}/chat/completions", json=payload)
            res.raise_for_status()
            data = res.json()
            latency = (time.time() - start_time) * 1000.0

            choices = data.get("choices", [])
            content = ""
            finish_reason = None
            if choices:
                choice = choices[0]
                content = choice.get("message", {}).get("content", "")
                finish_reason = choice.get("finish_reason")

            usage = data.get("usage", {})
            return CompletionResponse(
                content=content or "",
                model=model,
                provider=self.name,
                usage={
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                },
                finish_reason=finish_reason,
                latency_ms=latency
            )

    async def test_connection(self, model: str) -> Dict[str, Any]:
        try:
            res = await self.generate(
                messages=[{"role": "user", "content": "Respond with the single word 'OK'."}],
                model=model,
                max_tokens=10,
                timeout=15
            )
            return {
                "success": True,
                "latency_ms": res.latency_ms,
                "response": res.content.strip(),
                "provider": self.name,
                "model": model
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": self.name,
                "model": model
            }

