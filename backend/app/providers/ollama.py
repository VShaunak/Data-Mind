import httpx
import time
from typing import List, Dict, Any, Optional
from app.providers.base import LLMProvider, ModelInfo, CompletionResponse

class OllamaProvider(LLMProvider):
    name: str = "ollama"

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> List[ModelInfo]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = []
                    for m in data.get("models", []):
                        size_mb = m.get("size", 0) / (1024 * 1024)
                        size_str = f"{size_mb:.1f} MB" if size_mb < 1024 else f"{size_mb / 1024:.2f} GB"
                        models.append(
                            ModelInfo(
                                id=m.get("name", "unknown"),
                                name=m.get("name", "unknown"),
                                provider=self.name,
                                size=size_str,
                                modified_at=m.get("modified_at")
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
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "num_predict": max_tokens,
            }
        }
        if response_format == "json":
            payload["format"] = "json"

        async with httpx.AsyncClient(timeout=float(timeout)) as client:
            res = await client.post(f"{self.base_url}/api/chat", json=payload)
            res.raise_for_status()
            data = res.json()
            latency = (time.time() - start_time) * 1000.0

            content = data.get("message", {}).get("content", "")
            return CompletionResponse(
                content=content,
                model=model,
                provider=self.name,
                usage={
                    "prompt_eval_count": data.get("prompt_eval_count", 0),
                    "eval_count": data.get("eval_count", 0),
                },
                finish_reason="stop" if data.get("done") else None,
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

