from app.providers.openai_compatible import OpenAICompatibleProvider

class LlamaCppProvider(OpenAICompatibleProvider):
    name: str = "llamacpp"

    def __init__(self, base_url: str = "http://127.0.0.1:8080/v1"):
        super().__init__(base_url, name="llamacpp")

